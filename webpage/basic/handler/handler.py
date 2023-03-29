import os
import subprocess
homedir = os.getenv("HOME")

class Handler:
    def __init__(self):
        print("Initiating handler")

    def parse_text(self, text):
        split_pos = text.find(":")
        if not split_pos == -1:
            key   = text[:split_pos]
            value = text[split_pos+1:]
            return key, value
        else:
            return key, ""

    def call_command(self, text):
        self.key, self.value = self.parse_text(text)
        commands = {
            "info": self.info_function,
            "log": self.showlog_function,
            "datawall": self.create_datawall
        }

        if self.key in commands:
            result = commands[self.key](self.value)
            return result
        else:
            return "Unknown command"

    def info_function(self, info_module_name):
        if not "/" in info_module_name:
            if not "info_" in info_module_name:
                info_module_name = "info_" + info_module_name
            if not info_module_name[:3] == ".py":
                info_module_name = info_module_name + ".py"
            im_path = os.path.join(homedir, "Pigrow/scripts/gui/info_modules")
            info_module_path = os.path.join(im_path, info_module_name)

        text = "info module: " + info_module_path + "\n\n"
        text += self.run_local(info_module_path)

        return text

    def showlog_function(self, value):
        if not "/" in value:
            if not "." in value:
                value = value + ".txt"
            log_base_path = os.path.join(homedir, "Pigrow/logs/")
            log_to_load = os.path.join(log_base_path, value)
        else:
            log_to_load = value
        cmd = "tail -n 5 " + log_to_load
        return self.run_local(cmd)

    def create_datawall(self, value):
        if "+" in value:
            vsplit = value.split("+")
            preset = vsplit[0]
            module = vsplit[1]
        else:
            preset = value
            module = None
        # make cmd
        outpath = os.path.join(homedir, "Pigrow/graphs/webdatawall.png")
        cmd_path = os.path.join(homedir, "Pigrow/scripts/visualisation/modular_datawall.py")
        cmd = cmd_path +  " out=" + outpath + " preset=" + preset
        if not module == None:
            cmd += " module=" + module
        # make datawall
        output = self.run_local(cmd)
        if not module == None:
            return "webdatawall.png"
        else:
            return "datawall_graph_0.png"


    def run_local(self, cmd, timeout=30):
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.decode("utf-8")
            else:
                return "Error: " + result.stderr.decode("utf-8")
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
