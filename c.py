import subprocess
import time
import os
import threading

# 자동 드라이버 설치를 위한 라이브러리들
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    print("✅ Selenium과 webdriver-manager가 설치되어 있습니다.")
except ImportError as e:
    print("❌ 필요한 라이브러리가 설치되지 않았습니다.")
    print("설치 명령어:")
    print("pip install selenium webdriver-manager")
    SELENIUM_AVAILABLE = False

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    print("⚠️ schedule 라이브러리가 설치되지 않았습니다.")
    print("설치 명령어: pip install schedule")
    SCHEDULE_AVAILABLE = False

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
            if "device" in result.stdout and "device" in result.stdout.split():
                print("✅ 안드로이드 디바이스가 연결되어 있습니다.")
                return True
            else:
                print("❌ 안드로이드 디바이스가 연결되지 않았습니다.")
                return False
        except:
            print("❌ ADB가 설치되지 않았거나 경로에 없습니다.")
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
        
        original_status = self.get_airplane_mode_status()
        print(f"현재 비행기모드 상태: {'ON' if original_status else 'OFF'}")
        
        if self.set_airplane_mode(True):
            print(f"⏰ {duration}초 대기 중...")
            time.sleep(duration)
            
            if self.set_airplane_mode(False):
                print("✅ 비행기모드 사이클이 완료되었습니다.")
                return True
        
        return False

class AutoSeleniumBrowser:
    """자동 드라이버 설치가 포함된 Selenium 브라우저"""
    
    def __init__(self, headless=True):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium과 webdriver-manager가 설치되지 않았습니다.")
        
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome WebDriver 자동 설치 및 설정"""
        try:
            print("🔄 ChromeDriver 자동 설치 중...")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
                print("🔇 헤드리스 모드로 실행")
            
            # 안정성을 위한 옵션들
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # macOS에서 추가 옵션
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            
            # ChromeDriver 자동 다운로드 및 설치
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver 설치 완료: {driver_path}")
            
            # Service 객체 생성
            service = Service(driver_path)
            
            # WebDriver 초기화
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Selenium WebDriver가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            print(f"❌ WebDriver 초기화 실패: {e}")
            print("해결 방법:")
            print("1. Chrome 브라우저가 설치되어 있는지 확인")
            print("2. 인터넷 연결 확인 (ChromeDriver 다운로드 필요)")
            print("3. 방화벽 설정 확인")
            raise
    
    def visit_naver(self):
        """네이버 메인 페이지 방문"""
        try:
            print("🌐 네이버에 접속 중...")
            self.driver.get("https://www.naver.com")
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            title = self.driver.title
            print(f"✅ 네이버 접속 성공: {title}")
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            print(f"🔗 현재 URL: {current_url}")
            
            # 현재 시간 정보
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
            print(f"🔍 '{query}' 검색 중...")
            
            # 검색창 찾기 (여러 방법 시도)
            search_box = None
            selectors = [
                (By.ID, "query"),
                (By.NAME, "query"),
                (By.CSS_SELECTOR, "input[placeholder*='검색']"),
                (By.CSS_SELECTOR, ".search_input"),
                (By.CSS_SELECTOR, "#nx_query")
            ]
            
            for by, selector in selectors:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    print(f"✅ 검색창 발견: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                print("❌ 검색창을 찾을 수 없습니다.")
                return False
            
            # 검색어 입력
            search_box.clear()
            search_box.send_keys(query)
            
            # 검색 버튼 찾기 및 클릭
            search_buttons = [
                (By.CLASS_NAME, "btn_search"),
                (By.CSS_SELECTOR, ".search_btn"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.ID, "search_btn")
            ]
            
            search_clicked = False
            for by, selector in search_buttons:
                try:
                    search_button = self.driver.find_element(by, selector)
                    search_button.click()
                    search_clicked = True
                    print(f"✅ 검색 버튼 클릭: {selector}")
                    break
                except:
                    continue
            
            if not search_clicked:
                # Enter 키로 검색 시도
                from selenium.webdriver.common.keys import Keys
                search_box.send_keys(Keys.RETURN)
                print("✅ Enter 키로 검색 실행")
            
            # 검색 결과 페이지 로드 대기
            WebDriverWait(self.driver, 10).until(
                lambda driver: "search.naver.com" in driver.current_url or "검색결과" in driver.page_source
            )
            
            print(f"✅ '{query}' 검색 완료")
            print(f"🔗 검색 결과 URL: {self.driver.current_url}")
            
            return True
            
        except Exception as e:
            print(f"🔍 검색 실패: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        """스크린샷 저장"""
        try:
            if not filename:
                filename = f"naver_screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            print(f"📸 스크린샷 저장: {filename}")
            return filename
        except Exception as e:
            print(f"📸 스크린샷 실패: {e}")
            return None
    
    def get_page_info(self):
        """현재 페이지 정보 수집"""
        try:
            info = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'page_source_length': len(self.driver.page_source),
                'window_size': self.driver.get_window_size(),
                'time': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("📊 페이지 정보:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            return info
        except Exception as e:
            print(f"📊 페이지 정보 수집 실패: {e}")
            return None
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            try:
                self.driver.quit()
                print("🚪 브라우저가 종료되었습니다.")
            except:
                pass

class AutomatedController:
    def __init__(self):
        """자동화 컨트롤러 클래스"""
        self.android = AndroidAirplaneMode()
        self.browser = None
        self.running = False
    
    def check_prerequisites(self):
        """사전 요구사항 확인"""
        print("📋 사전 요구사항 확인 중...")
        
        # Selenium 확인
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium이 설치되지 않았습니다.")
            return False
        
        # ADB 연결 확인
        adb_ok = self.android.check_device_connection()
        
        # 브라우저 초기화 테스트
        try:
            print("🔧 브라우저 초기화 테스트 중...")
            test_browser = AutoSeleniumBrowser(headless=True)
            test_browser.close_browser()
            print("✅ 브라우저 테스트 완료")
            return adb_ok
        except Exception as e:
            print(f"❌ 브라우저 테스트 실패: {e}")
            return False
    
    def single_cycle(self, search_query=None, airplane_duration=5, take_screenshot=False):
        """단일 사이클 실행"""
        print(f"\n{'='*60}")
        print(f"🚀 Selenium 자동화 사이클 시작 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 1. 브라우저 초기화
            self.browser = AutoSeleniumBrowser(headless=True)
            
            # 2. 네이버 접속
            if not self.browser.visit_naver():
                print("❌ 네이버 접속 실패로 사이클 중단")
                self.browser.close_browser()
                return False
            
            # 3. 페이지 정보 수집
            self.browser.get_page_info()
            
            # 4. 검색 수행 (선택사항)
            if search_query:
                self.browser.search_naver(search_query)
                time.sleep(2)  # 검색 결과 확인을 위한 대기
            
            # 5. 스크린샷 (선택사항)
            if take_screenshot:
                self.browser.take_screenshot()
            
            # 6. 브라우저 종료
            self.browser.close_browser()
            
            # 7. 비행기모드 사이클
            airplane_success = self.android.airplane_mode_cycle(airplane_duration)
            
            if airplane_success:
                print("✅ 전체 사이클 완료")
                return True
            else:
                print("⚠️ 비행기모드 실패, 웹 접속은 성공")
                return True
                
        except Exception as e:
            print(f"❌ 사이클 실행 중 오류: {e}")
            if self.browser:
                self.browser.close_browser()
            return False
    
    def continuous_mode(self, interval_minutes=10, search_query=None):
        """연속 실행 모드"""
        print(f"\n🔄 연속 실행 모드 시작 (간격: {interval_minutes}분)")
        print("Ctrl+C를 눌러 중단할 수 있습니다.")
        
        self.running = True
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                print(f"\n📊 사이클 #{cycle_count} 시작")
                
                success = self.single_cycle(search_query)
                
                if success:
                    print(f"✅ 사이클 #{cycle_count} 완료")
                else:
                    print(f"❌ 사이클 #{cycle_count} 실패")
                
                if self.running:
                    print(f"⏰ {interval_minutes}분 대기 중... (다음 사이클: #{cycle_count + 1})")
                    time.sleep(interval_minutes * 60)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 중단되었습니다. (총 {cycle_count}회 실행)")
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        finally:
            self.running = False

def install_requirements():
    """필요한 라이브러리 자동 설치"""
    required_packages = [
        "selenium",
        "webdriver-manager",
        "schedule"
    ]
    
    print("📦 필요한 라이브러리 설치 중...")
    
    for package in required_packages:
        try:
            subprocess.run([
                "pip", "install", package
            ], check=True, capture_output=True)
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 설치 실패")

def main():
    """메인 실행 함수"""
    print("🤖 Selenium 자동 드라이버 설치 + 네이버 자동화")
    print("=" * 60)
    
    # 라이브러리 설치 확인
    if not SELENIUM_AVAILABLE:
        install_choice = input("필요한 라이브러리를 자동 설치하시겠습니까? (y/n): ").lower()
        if install_choice == 'y':
            install_requirements()
            print("설치 완료 후 프로그램을 다시 실행해주세요.")
            return
        else:
            print("수동 설치 명령어:")
            print("pip install selenium webdriver-manager schedule")
            return
    
    controller = AutomatedController()
    
    # 사전 요구사항 확인
    if not controller.check_prerequisites():
        print("\n❌ 사전 요구사항을 만족하지 않습니다.")
        return
    
    while True:
        print("\n" + "="*60)
        print("🎯 Selenium 자동화 모드 선택")
        print("="*60)
        print("1. 단일 실행 (기본)")
        print("2. 단일 실행 + 스크린샷")
        print("3. 연속 실행 모드")
        print("4. 비행기모드만 테스트")
        print("5. 브라우저만 테스트")
        print("0. 종료")
        
        choice = input("\n선택하세요 (0-5): ").strip()
        
        if choice == "1":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            
            controller.single_cycle(search_query, duration, False)
            
        elif choice == "2":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            
            controller.single_cycle(search_query, duration, True)
            
        elif choice == "3":
            search_query = input("검색어 입력 (없으면 엔터): ").strip()
            search_query = search_query if search_query else None
            
            interval = input("실행 간격(분, 기본값 10): ").strip()
            interval = int(interval) if interval.isdigit() else 10
            
            controller.continuous_mode(interval, search_query)
            
        elif choice == "4":
            duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            
            controller.android.airplane_mode_cycle(duration)
            
        elif choice == "5":
            try:
                print("🔧 브라우저 테스트 중...")
                browser = AutoSeleniumBrowser(headless=False)  # 헤드리스 끄기
                browser.visit_naver()
                browser.get_page_info()
                
                input("브라우저 창을 확인한 후 엔터를 눌러주세요...")
                browser.close_browser()
                
            except Exception as e:
                print(f"❌ 브라우저 테스트 실패: {e}")
            
        elif choice == "0":
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 올바른 번호를 선택해주세요.")

if __name__ == "__main__":
    main()