import subprocess
import os
import uuid

class LuaDeobfuscator:
    def __init__(self, work_dir="/tmp/lua_deobf"):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def save_temp_file(self, content, extension=".lua"):
        filename = f"{uuid.uuid4()}{extension}"
        path = os.path.join(self.work_dir, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def run_unluac_js(self, file_path):
        try:
            # تشغيل unluac-js باستخدام npx
            result = subprocess.run(["npx", "unluac-js", file_path], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return str(e)

    def run_prometheus(self, file_path):
        return "-- Prometheus Deobfuscation logic placeholder"

    def run_moonsec(self, file_path):
        return "-- MoonSec Deobfuscation logic placeholder"

    def run_luadec_rust(self, file_path):
        try:
            result = subprocess.run(["luadec", file_path], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except:
            return "luadec-rust not installed or not in PATH"

    def run_unluau(self, file_path):
        return "-- Unluau Decompiler placeholder"

    def run_cerbero(self, file_path):
        return "-- Cerbero Labs Lua Decompiler placeholder"

    def deobfuscate_all(self, content):
        file_path = self.save_temp_file(content)
        results = {}
        
        results['unluac-js'] = self.run_unluac_js(file_path)
        results['Prometheus'] = self.run_prometheus(file_path)
        results['MoonSec'] = self.run_moonsec(file_path)
        results['luadec-rust'] = self.run_luadec_rust(file_path)
        results['Unluau'] = self.run_unluau(file_path)
        results['Cerbero'] = self.run_cerbero(file_path)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return results
