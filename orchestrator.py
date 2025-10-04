import platform
import json
import sys
import os
from datetime import datetime
import subprocess
import locale

import requests


def get_system_info():
    system_data = {}

    # Основна інформація про ОС
    system_data['os'] = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture()[0],
        'node': platform.node()
    }

    # Інформація про Python (для налагодження)
    system_data['python'] = {
        'version': platform.python_version(),
        'implementation': platform.python_implementation()
    }

    # Інформація про CPU (базова)
    system_data['cpu'] = {
        'processor': platform.processor(),
        'machine': platform.machine()
    }

    # Платформо-специфічна інформація
    os_type = platform.system()
    if os_type == 'Windows':
        try:
            system_data['platform_specific'] = get_windows_info()
        except:
            system_data['platform_specific'] = {'error': 'Could not retrieve Windows info'}
    elif os_type == 'Darwin':  # macOS
        try:
            system_data['platform_specific'] = get_macos_info()
        except:
            system_data['platform_specific'] = {'error': 'Could not retrieve macOS info'}
    elif os_type == 'Linux':
        try:
            system_data['platform_specific'] = get_linux_info()
        except:
            system_data['platform_specific'] = {'error': 'Could not retrieve Linux info'}
    else:
        system_data['platform_specific'] = {'error': 'Unknown platform'}

    # Мова системи
    try:
        # Use getlocale() for language and getencoding() for encoding
        language, _ = locale.getlocale() or ('unknown', None)
        encoding = locale.getencoding() or 'unknown'
        system_data['locale'] = {
            'language': language,
            'encoding': encoding
        }
    except:
        system_data['locale'] = {
            'language': 'unknown',
            'encoding': 'unknown'
        }

    # Час збору даних
    system_data['timestamp'] = datetime.now().isoformat()

    return system_data


def get_windows_info():
    """Отримує додаткову інформацію для Windows через WMIC"""
    windows_info = {}

    try:
        # Інформація про CPU
        cpu_output = subprocess.check_output(
            'wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors /format:list',
            shell=True,
            text=True,
            timeout=5
        )
        cpu_data = parse_wmic_output(cpu_output)
        if cpu_data:
            windows_info['cpu'] = cpu_data

        # Інформація про RAM
        memory_output = subprocess.check_output(
            'wmic computersystem get TotalPhysicalMemory /format:list',
            shell=True,
            text=True,
            timeout=5
        )
        memory_data = parse_wmic_output(memory_output)
        if memory_data and 'TotalPhysicalMemory' in memory_data:
            total_gb = round(int(memory_data['TotalPhysicalMemory']) / (1024 ** 3), 2)
            windows_info['memory'] = {'total_gb': total_gb}

        # Інформація про комп'ютер
        cs_output = subprocess.check_output(
            'wmic computersystem get Manufacturer,Model /format:list',
            shell=True,
            text=True,
            timeout=5
        )
        cs_data = parse_wmic_output(cs_output)
        if cs_data:
            windows_info['computer'] = cs_data

        # Інформація про диски
        disk_output = subprocess.check_output(
            'wmic logicaldisk get DeviceID,Size,FreeSpace /format:list',
            shell=True,
            text=True,
            timeout=5
        )
        disks = parse_wmic_disks(disk_output)
        if disks:
            windows_info['disks'] = disks

    except Exception as e:
        windows_info['error'] = str(e)

    return windows_info


def parse_wmic_output(output):
    """Парсить вивід WMIC команди"""
    data = {}
    for line in output.split('\n'):
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                data[key] = value
    return data


def parse_wmic_disks(output):
    """Парсить інформацію про диски"""
    disks = []
    current_disk = {}

    for line in output.split('\n'):
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                current_disk[key] = value
        elif current_disk:
            # Закінчився блок диска
            if 'DeviceID' in current_disk:
                disk_info = {'device': current_disk['DeviceID']}
                if 'Size' in current_disk and current_disk['Size']:
                    disk_info['total_gb'] = round(int(current_disk['Size']) / (1024 ** 3), 2)
                if 'FreeSpace' in current_disk and current_disk['FreeSpace']:
                    disk_info['free_gb'] = round(int(current_disk['FreeSpace']) / (1024 ** 3), 2)
                disks.append(disk_info)
            current_disk = {}

    return disks


def get_macos_info():
    """Отримує інформацію для macOS"""
    macos_info = {}

    try:
        # Інформація про систему через system_profiler
        hw_output = subprocess.check_output(
            'system_profiler SPHardwareDataType',
            shell=True,
            text=True,
            timeout=10
        )

        # Парсимо вивід
        for line in hw_output.split('\n'):
            line = line.strip()
            if 'Model Name' in line:
                macos_info['model'] = line.split(':', 1)[1].strip()
            elif 'Chip' in line or 'Processor Name' in line:
                macos_info['processor'] = line.split(':', 1)[1].strip()
            elif 'Total Number of Cores' in line:
                macos_info['cores'] = line.split(':', 1)[1].strip()
            elif 'Memory' in line:
                macos_info['memory'] = line.split(':', 1)[1].strip()

        # Інформація про диски
        df_output = subprocess.check_output(
            'df -h /',
            shell=True,
            text=True,
            timeout=5
        )
        lines = df_output.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 4:
                macos_info['disk'] = {
                    'total': parts[1],
                    'used': parts[2],
                    'available': parts[3]
                }

    except Exception as e:
        macos_info['error'] = str(e)

    return macos_info


def get_linux_info():
    """Отримує інформацію для Linux"""
    linux_info = {}

    try:
        # CPU інформація з /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                for line in cpuinfo.split('\n'):
                    if 'model name' in line:
                        linux_info['cpu_model'] = line.split(':', 1)[1].strip()
                        break
                cores = cpuinfo.count('processor')
                linux_info['cpu_cores'] = cores
        except:
            pass

        # Інформація про пам'ять з /proc/meminfo
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemTotal' in line:
                        mem_kb = int(line.split()[1])
                        linux_info['memory_gb'] = round(mem_kb / (1024 ** 2), 2)
                        break
        except:
            pass

        # Інформація про диски
        try:
            df_output = subprocess.check_output(
                'df -h /',
                shell=True,
                text=True,
                timeout=5
            )
            lines = df_output.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    linux_info['disk'] = {
                        'total': parts[1],
                        'used': parts[2],
                        'available': parts[3]
                    }
        except:
            pass

        # Дистрибутив Linux
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME'):
                        linux_info['distribution'] = line.split('=', 1)[1].strip().strip('"')
                        break
        except:
            pass

    except Exception as e:
        linux_info['error'] = str(e)

    return linux_info

def get_output_path(filename):
    if getattr(sys, 'frozen', False):
        if sys.platform == "darwin":
            app_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", "..", ".."))
            return os.path.join(app_dir, filename)
        else:
            return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        # Якщо .py
        return os.path.join(os.path.dirname(__file__), filename)


def get_lua_script_from_llm(system_info, api_key, api_provider='openai'):
    """
    Отримує Lua скрипт від LLM на основі системної інформації

    Args:
        system_info: Словник з інформацією про систему
        api_key: API ключ для LLM
        api_provider: Провайдер API ('openai', 'anthropic', 'google')

    Returns:
        str: Lua скрипт або None у разі помилки
    """
    try:
        prompt = f"""Generate a Lua script that displays system information.
                System Information:
                - OS: {system_info['os']['system']} {system_info['os']['release']}
                - Architecture: {system_info['os']['architecture']}
                - Processor: {system_info['cpu']['processor']}
                Create a simple Lua script that prints this information."""

        if api_provider == 'openai':
            url = 'https://api.openai.com/v1/responses'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "gpt-4.1-mini",
                "input": [
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": "You are a helpful assistant that generates Lua scripts."}]
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}]
                    }
                ],
                "temperature": 0.7,
                "max_output_tokens": 1000
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            lua_script = response.json()["output"][0]["content"][0]["text"]


        elif api_provider == 'anthropic':
            # Anthropic Claude API
            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1024,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            lua_script = response.json()['content'][0]['text']

        elif api_provider == 'google':
            # Google Gemini API
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'
            headers = {'Content-Type': 'application/json'}
            data = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }]
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            lua_script = response.json()['candidates'][0]['content']['parts'][0]['text']

        else:
            raise ValueError(f"Unknown API provider: {api_provider}")

        # Витягуємо тільки Lua код, якщо він обгорнутий в markdown
        if '```lua' in lua_script:
            lua_script = lua_script.split('```lua')[1].split('```')[0].strip()
        elif '```' in lua_script:
            lua_script = lua_script.split('```')[1].split('```')[0].strip()

        return lua_script

    except Exception as e:
        print(f"Error getting Lua script from LLM: {e}")
        return None


def save_lua_script(lua_script, filename='generated_script.lua'):
    """Зберігає Lua скрипт у файл"""
    if lua_script:
        filepath = get_output_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(lua_script)
        return filepath
    return None


def save_to_json(data, filename='system_info.json'):
    """Зберігає дані у JSON файл"""
    filepath = get_output_path(filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath



def main():
    try:
        system_info = get_system_info()
        json_path = save_to_json(system_info)
        api_key = 'YOUR_API_KEY'.strip()
        api_provider = 'openai'
        if api_key:
            lua_script = get_lua_script_from_llm(system_info, api_key, api_provider)
            if lua_script:
                lua_path = save_lua_script(lua_script)
                print(f"Lua script saved to: {lua_path}")
        else:
            print("No API key found. Skipping Lua script generation.")
        return 0

    except Exception as e:
        try:
            error_path = get_output_path('error.log')
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(f"Помилка: {type(e).__name__}\n")
                f.write(f"Деталі: {str(e)}\n")
                import traceback
                f.write(f"\nТрейсбек:\n{traceback.format_exc()}")
        except:
            pass
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)