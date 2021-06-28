#!/usr/bin/python3
import os
import sys
import shutil
import datetime

print("Creating pigrow diagnostic information bundle")
print("")
print(" This gathers a selection of information from the pigrow and packages it")
print(" so that it can be sent to me or the community for help diagnosing setup ")
print(" issues and problems.")
print("")
print(" This does not include dirlocs.txt or any personal or password information")
print("")

f_path = os.path.dirname(os.path.abspath(__file__))
if "Pigrow" in f_path:
    pigrow_path = f_path.split('Pigrow')[0] + 'Pigrow/'
else:
    print(" Unable to locate Pigrow folder")
    sys.exit()


bundle_folder = os.path.join(pigrow_path, "temp/diagnostic_bundle/")

if os.path.isdir(bundle_folder):
    shutil.rmtree(bundle_folder)
os.makedirs(bundle_folder)

info_modules_to_read = ['info_control_config.py',
                        'info_dirlocs_check.py',
                        'info_diskusage.py',
                        'info_git_update.py',
                        'info_power_warnings.py',
                        'info_os_version.py',
                        'info_hardware_version.py']

files_to_copy = ['logs/selflog.txt',
                 'logs/adv_selflog.txt',
                 'logs/switch_log.txt',
                 'logs/err_log.txt',
                 'config/pigrow_config.txt',
                 'config/trigger_events.txt',
                 'logs/trigger_conditons.txt']

def write_cron_text(bundle_folder):
    out =  os.popen("contab -l").read()
    cron_text_path = os.path.join(bundle_folder, "cron_text.txt")
    with open(cron_text_path, "w") as f:
        f.write(out)
    print("\nCron text written to " + cron_text_path)

def create_info_file(info_modules_to_read, bundle_folder):
    info_text = "Info modules read " + str(datetime.datetime.now()) + "\n\n"
    for info in info_modules_to_read:
        info_text += info + "\n"
        info_module_path = os.path.join(pigrow_path, "scripts/gui/info_modules/" + info)
        out =  os.popen(info_module_path).read()
        for line in out.splitlines():
            info_text += "    " + line + '\n'
        info_text += "\n"

    file_path = os.path.join(bundle_folder, "info_module_text.txt")
    with open(file_path, "w") as f:
        f.write(info_text)
    print("\nInfo module text written to " + file_path)

def copy_files_to_bundle(files_to_copy, bundle_folder):
    print(" Copying files to bundle ")
    for file in files_to_copy:
        file_path = os.path.join(pigrow_path, file)
        if os.path.isfile(file_path):
            dest_path = os.path.join(bundle_folder, file.split("/")[1])
            shutil.copyfile(file_path, dest_path)
            print(" Copied", file_path, dest_path)
        else:
            print(" no ", file_path)

if __name__ == '__main__':
    write_cron_text(bundle_folder)
    create_info_file(info_modules_to_read, bundle_folder)
    copy_files_to_bundle(files_to_copy, bundle_folder)
    zip_path = os.path.join(pigrow_path, "graphs/diagnostic_bundle")
    shutil.make_archive(zip_path, 'zip', bundle_folder)
    print("\nDiagnostic Bundle saved to ", zip_path + ".zip")
