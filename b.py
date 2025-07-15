import subprocess
import time
import os

#ADB 설치: Android SDK Platform Tools를 설치하여 ADB(Android Debug Bridge)를 사용할 수 있어야 합니다

class AndroidAirplaneMode:
    def __init__(self, device_id=None):
        """
        안드로이드 비행기모드 제어 클래스
        device_id: 특정 디바이스 ID (여러 디바이스 연결시 사용)
        """
        self.device_id = device_id
        self.adb_prefix = f"adb -s {device_id}" if device_id else "adb"
    
    def check_device_connection(self):
        """디바이스 연결 상태 확인"""
        try:
            result = subprocess.run([self.adb_prefix.split()[0], "devices"], 
                                  capture_output=True, text=True)
            if "device" in result.stdout:
                print("✓ 안드로이드 디바이스가 연결되어 있습니다.")
                return True
            else:
                print("✗ 안드로이드 디바이스가 연결되지 않았습니다.")
                return False
        except:
            print("✗ ADB가 설치되지 않았거나 경로에 없습니다.")
            return False
    
    def get_airplane_mode_status(self):
        """현재 비행기모드 상태 확인"""
        try:
            cmd = f"{self.adb_prefix} shell settings get global airplane_mode_on"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            status = result.stdout.strip()
            return status == "1"
        except Exception as e:
            print(f"상태 확인 중 오류: {e}")
            return None
    
    def set_airplane_mode(self, enable=True):
        """비행기모드 설정"""
        try:
            # 비행기모드 설정 변경
            mode_value = "1" if enable else "0"
            cmd1 = f"{self.adb_prefix} shell settings put global airplane_mode_on {mode_value}"
            subprocess.run(cmd1.split(), check=True)
            
            # 브로드캐스트 전송으로 설정 적용
            cmd2 = f"{self.adb_prefix} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state {str(enable).lower()}"
            subprocess.run(cmd2.split(), check=True)
            
            action = "활성화" if enable else "비활성화"
            print(f"✓ 비행기모드가 {action}되었습니다.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 비행기모드 설정 중 오류: {e}")
            return False
        except Exception as e:
            print(f"✗ 예상치 못한 오류: {e}")
            return False
    
    def toggle_airplane_mode(self):
        """비행기모드 토글 (현재 상태의 반대로 전환)"""
        current_status = self.get_airplane_mode_status()
        if current_status is None:
            return False
        
        new_status = not current_status
        return self.set_airplane_mode(new_status)
    
    def airplane_mode_cycle(self, duration=5):
        """비행기모드를 켰다가 끄는 사이클"""
        print("비행기모드 사이클 시작...")
        
        # 현재 상태 확인
        original_status = self.get_airplane_mode_status()
        print(f"현재 비행기모드 상태: {'ON' if original_status else 'OFF'}")
        
        # 비행기모드 켜기
        if self.set_airplane_mode(True):
            print(f"{duration}초 대기 중...")
            time.sleep(duration)
            
            # 비행기모드 끄기
            if self.set_airplane_mode(False):
                print("✓ 비행기모드 사이클이 완료되었습니다.")
                return True
        
        return False

# 사용 예제
def main():
    # 안드로이드 디바이스 제어 객체 생성
    android = AndroidAirplaneMode()
    
    # 디바이스 연결 확인
    if not android.check_device_connection():
        print("먼저 USB 디버깅을 활성화하고 디바이스를 연결해주세요.")
        return
    
    # 현재 상태 확인
    current_status = android.get_airplane_mode_status()
    if current_status is not None:
        print(f"현재 비행기모드: {'ON' if current_status else 'OFF'}")
    
    # 메뉴 선택
    while True:
        print("\n=== 안드로이드 비행기모드 제어 ===")
        print("1. 비행기모드 켜기")
        print("2. 비행기모드 끄기")
        print("3. 비행기모드 토글")
        print("4. 비행기모드 사이클 (켜기→끄기)")
        print("5. 현재 상태 확인")
        print("0. 종료")
        
        choice = input("선택하세요: ").strip()
        
        if choice == "1":
            android.set_airplane_mode(True)
        elif choice == "2":
            android.set_airplane_mode(False)
        elif choice == "3":
            android.toggle_airplane_mode()
        elif choice == "4":
            duration = input("대기 시간(초, 기본값 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            android.airplane_mode_cycle(duration)
        elif choice == "5":
            status = android.get_airplane_mode_status()
            if status is not None:
                print(f"현재 비행기모드: {'ON' if status else 'OFF'}")
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 선택해주세요.")

# 자동화 예제
def automation_example():
    """자동화 예제: 네트워크 재연결을 위한 비행기모드 사이클"""
    android = AndroidAirplaneMode()
    
    if android.check_device_connection():
        print("네트워크 재연결을 위한 비행기모드 사이클 실행...")
        android.airplane_mode_cycle(3)  # 3초 대기
        print("네트워크 재연결 완료!")

if __name__ == "__main__":
    main()
    # automation_example()  # 자동화 예제 실행시 주석 해제