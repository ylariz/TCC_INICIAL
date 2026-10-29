import os
import signal
import subprocess
import sys
import textwrap
import traceback


LIMITE_SEGUNDOS = 5

ESPERA_LIMPEZA_SEGUNDOS = 2

MENSAGEM_TIMEOUT = "Execução interrompida: limite de tempo excedido."

NO_WINDOWS = os.name == "nt"


if NO_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    _PROCESS_SET_QUOTA = 0x0100
    _PROCESS_TERMINATE = 0x0001

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [(nome, ctypes.c_ulonglong) for nome in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BASIC_LIMIT_INFORMATION),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.CreateJobObjectW.argtypes = (wintypes.LPVOID, wintypes.LPCWSTR)
    _kernel32.SetInformationJobObject.restype = wintypes.BOOL
    _kernel32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    _kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    _kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    _kernel32.TerminateJobObject.restype = wintypes.BOOL
    _kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

    def _criar_job_para(pid):
        job = _kernel32.CreateJobObjectW(None, None)
        if not job:
            return None

        info = _EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        configurou = _kernel32.SetInformationJobObject(
            job, _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info), ctypes.sizeof(info))

        processo = _kernel32.OpenProcess(_PROCESS_SET_QUOTA | _PROCESS_TERMINATE, False, pid)
        colocou = bool(processo) and _kernel32.AssignProcessToJobObject(job, processo)
        if processo:
            _kernel32.CloseHandle(processo)

        if not (configurou and colocou):
            _kernel32.CloseHandle(job)
            return None
        return job

    def _fechar_job(job):
        if job:
            _kernel32.TerminateJobObject(job, 1)
            _kernel32.CloseHandle(job)


def _opcoes_de_processo():
    if NO_WINDOWS:
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _encerrar_tudo(processo, job):
    if NO_WINDOWS:
        if job:
            _fechar_job(job)
        else:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(processo.pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=ESPERA_LIMPEZA_SEGUNDOS)
            except Exception:
                pass
    else:
        try:
            os.killpg(processo.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    try:
        processo.kill()
    except OSError:
        pass


def _recolher_saida(processo):
    try:
        saida, _ = processo.communicate(timeout=ESPERA_LIMPEZA_SEGUNDOS)
        return saida or ""
    except subprocess.TimeoutExpired:
        for canal in (processo.stdout, processo.stdin):
            try:
                if canal:
                    canal.close()
            except OSError:
                pass
        try:
            processo.wait(timeout=ESPERA_LIMPEZA_SEGUNDOS)
        except subprocess.TimeoutExpired:
            pass
        return ""


def executar_codigo(codigo, entrada):
    wrapper = f"""
        import sys
        import traceback

        sys.stdin.read(1)

        codigo = {codigo!r}
        entrada = {entrada!r}

        entradas = entrada.splitlines()


        def inputs(mensagem=""):
            if not entradas:
                raise RuntimeError("Não há mais entradas disponíveis.")

            return entradas.pop(0)


        try:
            exec(codigo, {{"input": inputs}})

        except Exception:
            print(traceback.format_exc(), end="")
        """

    processo = None
    job = None

    try:
        processo = subprocess.Popen(
            [sys.executable, "-u", "-c", textwrap.dedent(wrapper)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            **_opcoes_de_processo()
        )

        if NO_WINDOWS:
            job = _criar_job_para(processo.pid)

        try:
            saida, _ = processo.communicate(input="x", timeout=LIMITE_SEGUNDOS)

        except subprocess.TimeoutExpired:
            _encerrar_tudo(processo, job)
            job = None
            saida = _recolher_saida(processo)

            return {
                "sucesso": False,
                "saida": saida,
                "erro": MENSAGEM_TIMEOUT
            }

        _encerrar_tudo(processo, job)
        job = None

        return {
            "sucesso": processo.returncode == 0,
            "saida": saida,
            "erro": None if processo.returncode == 0 else saida
        }

    except Exception:
        if processo is not None:
            _encerrar_tudo(processo, job)
        return {
            "sucesso": False,
            "saida": "",
            "erro": traceback.format_exc()
        }
