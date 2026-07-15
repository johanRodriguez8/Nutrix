import time
import paramiko
import random
import threading

class RobotLoader:
    def __init__(self, name, ip, user, password, program_dir):
        self.name = name
        self.ip = ip
        self.user = user
        self.password = password
        self.program_dir = program_dir.rstrip("/")

        self.ssh_client = None
        self.sftp = None
        self.connected = False
        self.auto_mode = False
        self.cycle_count = 0

    # ================= CONNECTION =================
    def connect(self):
        # Prevent concurrent connect attempts
        if not hasattr(self, "_ssh_lock"):
            self._ssh_lock = threading.Lock()

        with self._ssh_lock:

            # If already connected and transport active, do nothing
            if getattr(self, "ssh_client", None):
                transport = self.ssh_client.get_transport()
                if transport and transport.is_active():
                    self.connected = True
                    return True

            # Clean previous connection if it exists
            try:
                if getattr(self, "sftp", None):
                    self.sftp.close()
            except:
                pass

            try:
                if getattr(self, "ssh_client", None):
                    self.ssh_client.close()
            except:
                pass

            try:
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self.ssh_client.connect(
                    hostname=self.ip,
                    username=self.user,
                    password=self.password,
                    timeout=10
                )

                self.sftp = self.ssh_client.open_sftp()
                self.connected = True

                print(f"{self.name} conectado correctamente")
                return True

            except Exception as e:
                self.connected = False
                print(f"{self.name} ERROR conexión: {e}")
                return False

    # ================= LIST PROGRAMS (.ngc ONLY) =================
    def list_programs(self):
        if not self.connected:
            return []
        try:
            files = self.sftp.listdir(self.program_dir)
            return [f for f in files if f.lower().endswith(".ngc")]
        except Exception as e:
            print(f"{self.name} ERROR listando programas: {e}")
            return []

    # ================= LOAD PROGRAM =================
    def load_program(self, program_name):
        full_path = f"{self.program_dir}/{program_name}"
        script = f"""
import linuxcnc, time
c = linuxcnc.command()
c.mode(linuxcnc.MODE_AUTO)
time.sleep(0.2)
c.program_open("{full_path}")
print("OK")
"""
        return self._run_script(script)

    # ================= CYCLE START =================
    def run_program(self):
        script = """
import linuxcnc, time
c = linuxcnc.command()
c.mode(linuxcnc.MODE_AUTO)
time.sleep(0.2)
c.auto(linuxcnc.AUTO_RUN, 0)
print("RUN")
"""
        return self._run_script(script)

       # ================= CYCLE STOP =================
    def stop_program(self):
        script = """
import linuxcnc, time
c = linuxcnc.command()
c.mode(linuxcnc.MODE_AUTO)
time.sleep(0.2)
c.abort
print("STOP PROGRAM")
"""
        return self._run_script(script)

    # ================= WAIT FINISH =================
    def wait_until_finished(self):
        script = """
import linuxcnc, time
s = linuxcnc.stat()
while True:
    s.poll()
    if s.interp_state == linuxcnc.INTERP_IDLE:
        print("DONE")
        break
    time.sleep(0.2)
"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("python3 -")
            stdin.write(script)
            stdin.channel.shutdown_write()
            return stdout.read().decode().strip()
        except:
            return "ERROR"

    # ================= AUTO SIMPLE =================
    def auto_random_cycle(self, cycle_counter):
        if not self.connected:
            return

        self.cycle_count = 0

        while self.auto_mode:
            programs = self.list_programs()
            if not programs:
                print(f"{self.name} No hay programas .ngc")
                time.sleep(1)
                continue

            program = random.choice(programs)

            if not self.load_program(program):
                print(f"{self.name} Error cargando programa {program}")
                break

            if not self.run_program():
                print(f"{self.name} Error en Cycle Start")
                break

            result = self.wait_until_finished()
            if result != "DONE":
                print(f"{self.name} Watchdog detectó: {result}")
                break

            self.cycle_count += 1
            cycle_counter.setText(f"CICLOS: {self.cycle_count}")
            time.sleep(1)

        self.auto_mode = False
        print(f"{self.name} AUTO detenido")

    # ================= RUN SCRIPT =================
    def _run_script(self, script):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("python3 -")
            stdin.write(script)
            stdin.channel.shutdown_write()
            err = stderr.read().decode()
            if err:
                print(f"{self.name} ERROR: {err}")
                return False
            return True
        except:
            return False
    def stopConnection(self):
        if not hasattr(self, "ssh_client"):
            self.ssh_client.close()