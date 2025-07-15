import subprocess
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading
import schedule

class AndroidAirplaneMode:
    def __init__(self, device_id=None):
        """안드로이드 비행기모드 제어 클래스"""
        self.device_id = device_id
        self.adb_prefix = f"adb -s {device_id}" if device_id else "adb"
    
    def check_device_connection(self):
        """디바이스 연결 상태 확인"""
        try:
            result = subprocess.run([self.adb_prefix.split()[0], "devices"], 
                                  capture_output=True, text=True)
            if "device" in result.stdout:
                return True
            return False
        except:
            return False
    
    def get_airplane_mode_status(self):
        """현재 비행기모드 상태 확인"""
        try:
            cmd = f"{self.adb_prefix} shell settings get global airplane_mode_on"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            status = result.stdout.strip()
            return status == "1"
        except:
            return None
    
    def set_airplane_mode(self, enable=True):
        """비행기모드 설정"""
        try:
            mode_value = "1" if enable else "0"
            cmd1 = f"{self.adb_prefix} shell settings put global airplane_mode_on {mode_value}"
            subprocess.run(cmd1.split(), check=True)
            
            cmd2 = f"{self.adb_prefix} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state {str(enable).lower()}"
            subprocess.run(cmd2.split(), check=True)
            
            action = "활성화" if enable else "비활성화"
            print(f"✓ 비행기모드가 {action}되었습니다.")
            return True
            
        except Exception as e:
            print(f"✗ 비행기모드 설정 중 오류: {e}")
            return False
    
    def airplane_mode_cycle(self, duration=5):
        """비행기모드를 켰다가 끄는 사이클"""
        print("🔄 비행기모드 사이클 시작...")
        
        # 비행기모드 켜기
        if self.set_airplane_mode(True):
            print(f"⏰ {duration}초 대기 중...")
            time.sleep(duration)
            
            # 비행기모드 끄기
            if self.set_airplane_mode(False):
                print("✅ 비행기모드 사이클이 완료되었습니다.")
                return True
        
        return False

class NaverBrowser:
    def __init__(self, headless=True):
        """네이버 가상브라우저 제어 클래스"""
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")  # 백그라운드 실행
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("✅ Chrome WebDriver가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            print(f"✗ WebDriver 초기화 실패: {e}")
            print("ChromeDriver가 설치되어 있고 PATH에 있는지 확인해주세요.")
    
    def visit_naver(self):
        """네이버 메인 페이지 방문"""
        try:
            print("🌐 네이버에 접속 중...")
            self.driver.get("https://www.naver.com")
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            title = self.driver.title
            print(f"✅ 네이버 접속 성공: {title}")
            
            # 현재 시간 정보 수집
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"📅 접속 시간: {current_time}")
            
            return True
            
        except TimeoutException:
            print("⏰ 네이버 접속 시간 초과")
            return False
        except WebDriverException as e:
            print(f"🌐 네이버 접속 실패: {e}")
            return False
    
    def search_naver(self, query):
        """네이버에서 검색"""
        try:
            # 검색창 찾기
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "query"))
            )
            
            # 검색어 입력
            search_box.clear()
            search_box.send_keys(query)
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.CLASS_NAME, "btn_search")
            search_button.click()
            
            # 검색 결과 페이지 로드 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "main_pack"))
            )
            
            print(f"🔍 '{query}' 검색 완료")
            return True
            
        except Exception as e:
            print(f"🔍 검색 실패: {e}")
            return False
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("🚪 브라우저가 종료되었습니다.")

class AutomatedController:
    def __init__(self):
        """자동화 컨트롤러 클래스"""
        self.android = AndroidAirplaneMode()
        self.browser = None
        self.running = False
    
    def check_prerequisites(self):
        """사전 요구사항 확인"""
        print("📋 사전 요구사항 확인 중...")
        
        # ADB 연결 확인
        if not self.android.check_device_connection():
            print("❌ 안드로이드 디바이스가 연결되지 않았습니다.")
            print("   USB 디버깅을 활성화하고 디바이스를 연결해주세요.")
            return False
        
        print("✅ 안드로이드 디바이스 연결 확인")
        
        # 브라우저 초기화 테스트
        try:
            test_browser = NaverBrowser(headless=True)
            test_browser.close_browser()
            print("✅ Chrome WebDriver 확인")
            return True
        except:
            print("❌ Chrome WebDriver 초기화 실패")
            return False
    
    def single_cycle(self, search_query=None, airplane_duration=5):
        """단일 사이클 실행"""
        print(f"\n{'='*50}")
        print(f"🚀 자동화 사이클 시작 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # 1. 브라우저 초기화
        self.browser = NaverBrowser(headless=True)
        
        # 2. 네이버 접속
        if not self.browser.visit_naver():
            print("❌ 네이버 접속 실패로 사이클 중단")
            self.browser.close_browser()
            return False
        
        # 3. 검색 수행 (선택사항)
        if search_query:
            self.browser.search_naver(search_query)
            time.sleep(2)  # 검색 결과 확인을 위한 대기
        
        # 4. 브라우저 종료
        self.browser.close_browser()
        
        # 5. 비행기모드 사이클
        success = self.android.airplane_mode_cycle(airplane_duration)
        
        if success:
            print("✅ 사이클 완료")
        else:
            print("❌ 사이클 실패")
        
        return success
    
    def continuous_mode(self, interval_minutes=10, search_query=None):
        """연속 실행 모드"""
        print(f"\n🔄 연속 실행 모드 시작 (간격: {interval_minutes}분)")
        print("Ctrl+C를 눌러 중단할 수 있습니다.")
        
        self.running = True
        
        try:
            while self.running:
                self.single_cycle(search_query)
                
                if self.running:
                    print(f"⏰ {interval_minutes}분 대기 중...")
                    time.sleep(interval_minutes * 60)
                    
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        finally:
            self.running = False
    
    def scheduled_mode(self, schedule_times, search_query=None):
        """예약 실행 모드"""
        print(f"📅 예약 실행 모드 설정 중...")
        
        # 스케줄 등록
        for time_str in schedule_times:
            schedule.every().day.at(time_str).do(
                self.single_cycle, search_query=search_query
            )
            print(f"⏰ {time_str}에 실행 예약됨")
        
        print("📅 예약 실행 모드 시작 (Ctrl+C로 중단)")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
        except KeyboardInterrupt:
            print("\n🛑 예약 실행이 중단되었습니다.")

def main():
    """메인 실행 함수"""
    controller = AutomatedController()
    
    print("🤖 네이버 접속 + 비행기모드 자동 제어 프로그램")
    print("=" * 50)
    
    # 사전 요구사항 확인
    if not controller.check_prerequisites():
        print("\n❌ 사전 요구사항을 만족하지 않습니다.")
        print("다음을 확인해주세요:")
        print("1. 안드로이드 디바이스 USB 디버깅 활성화")
        print("2. ChromeDriver 설치 및 PATH 설정")
        return
    
    while True:
        print("\n" + "="*50)
        print("🎯 실행 모드 선택")
        print("="*50)
        print("1. 단일 실행 (한 번만 실행)")
        print("2. 연속 실행 (주기적 반복)")
        print("3. 예약 실행 (특정 시간에 실행)")
        print("4. 설정 테스트")
        print("0. 종료")
        
        choice = input("\n선택하세요 (0-4): ").strip()
        
        if choice == "1":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            
            controller.single_cycle(search_query, duration)
            
        elif choice == "2":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            interval = input("실행 간격(분, 기본값 10): ").strip()
            interval = int(interval) if interval.isdigit() else 10
            
            controller.continuous_mode(interval, search_query)
            
        elif choice == "3":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            times_input = input("실행 시간들 입력 (예: 09:00,12:00,18:00): ").strip()
            schedule_times = [t.strip() for t in times_input.split(",") if t.strip()]
            
            if schedule_times:
                controller.scheduled_mode(schedule_times, search_query)
            else:
                print("❌ 올바른 시간 형식을 입력해주세요.")
                
        elif choice == "4":
            print("\n🔧 설정 테스트 중...")
            controller.check_prerequisites()
            
        elif choice == "0":
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 올바른 번호를 선택해주세요.")

if __name__ == "__main__":
    main()