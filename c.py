#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 자동 접속 + 안드로이드 비행기모드 제어 프로그램
- Selenium WebDriver 자동 설치
- 브라우저 유지/새로시작 옵션
- 반복 실행 및 무제한 연속 실행
- 테스트 모드 (안드로이드 기능 제외)
"""

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
    """안드로이드 비행기모드 제어 클래스"""
    
    def __init__(self, device_id=None):
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
                # chrome_options.add_argument("--headless")
                print("🔇 헤드리스 모드로 실행")
            else:
                print("🖥️ 브라우저 창이 화면에 표시됩니다")
            
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
                # 모든 창 닫기
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                
                # WebDriver 완전 종료
                self.driver.quit()
                print("🚪 브라우저가 완전히 종료되었습니다.")
                
                # 프로세스 강제 종료 (macOS/Linux)
                try:
                    import psutil
                    for proc in psutil.process_iter(['pid', 'name']):
                        if 'chrome' in proc.info['name'].lower() and 'chromedriver' in ' '.join(proc.cmdline()).lower():
                            proc.terminate()
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ 브라우저 종료 중 오류: {e}")
                # 강제 종료 시도
                try:
                    self.driver.quit()
                except:
                    pass
                
                # macOS에서 Chrome 프로세스 강제 종료
                try:
                    subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                    subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                    print("🔴 브라우저 프로세스 강제 종료")
                except:
                    pass
            finally:
                self.driver = None

class AutomatedController:
    """자동화 컨트롤러 클래스"""
    
    def __init__(self):
        self.android = AndroidAirplaneMode()
        self.browser = None
        self.running = False
    
    def check_prerequisites(self, test_mode=False):
        """사전 요구사항 확인"""
        print("📋 사전 요구사항 확인 중...")
        
        # Selenium 확인
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium이 설치되지 않았습니다.")
            return False
        
        # 테스트 모드가 아닌 경우에만 ADB 확인
        adb_ok = True
        if not test_mode:
            adb_ok = self.android.check_device_connection()
        else:
            print("🧪 테스트 모드: 안드로이드 디바이스 확인을 건너뜁니다.")
        
        # 브라우저 초기화 테스트
        try:
            print("🔧 브라우저 초기화 테스트 중...")
            test_browser = AutoSeleniumBrowser(headless=True)
            test_browser.close_browser()
            print("✅ 브라우저 테스트 완료")
            return adb_ok if not test_mode else True
        except Exception as e:
            print(f"❌ 브라우저 테스트 실패: {e}")
            return False
    
    def single_cycle(self, search_query=None, airplane_duration=5, take_screenshot=False, test_mode=False, browser_instance=None, cycle_number=1):
        """단일 사이클 실행"""
        print(f"\n{'='*60}")
        if test_mode:
            print(f"🧪 테스트 모드 - 사이클 #{cycle_number} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"🚀 일반 모드 - 사이클 #{cycle_number} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 브라우저 인스턴스가 전달되지 않은 경우 새로 생성
        create_new_browser = browser_instance is None
        
        try:
            # 1. 브라우저 초기화 또는 기존 브라우저 사용
            if create_new_browser:
                self.browser = AutoSeleniumBrowser(headless=test_mode)
                print("🌐 새 브라우저 인스턴스 생성")
            else:
                self.browser = browser_instance
                print("🌐 기존 브라우저 인스턴스 사용")
            
            # 2. 네이버 접속
            if not self.browser.visit_naver():
                print("❌ 네이버 접속 실패로 사이클 중단")
                if create_new_browser:
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
                screenshot_name = f"cycle_{cycle_number}_{int(time.time())}.png"
                self.browser.take_screenshot(screenshot_name)
            
            # 테스트 모드에서는 사용자가 확인할 시간 제공 (단일 실행시에만)
            if test_mode and create_new_browser and not browser_instance:
                input("\n🔍 브라우저 창을 확인한 후 엔터를 눌러 계속하세요...")
            
            # 6. 브라우저 종료 (새로 생성한 경우에만)
            if create_new_browser:
                time.sleep(1)  # 1초 대기 후 종료
                self.browser.close_browser()
                print("🚪 브라우저 종료")
                time.sleep(2)  # 종료 완료 대기
            else:
                print("🌐 브라우저 유지 (다음 사이클에서 재사용)")
            
            # 7. 비행기모드 사이클 (테스트 모드가 아닐 때만)
            if not test_mode:
                airplane_success = self.android.airplane_mode_cycle(airplane_duration)
                
                if airplane_success:
                    print("✅ 전체 사이클 완료")
                    return True
                else:
                    print("⚠️ 비행기모드 실패, 웹 접속은 성공")
                    return True
            else:
                print("🧪 테스트 모드 완료 - 안드로이드 기능 건너뜀")
                return True
                
        except Exception as e:
            print(f"❌ 사이클 실행 중 오류: {e}")
            if create_new_browser and self.browser:
                try:
                    time.sleep(1)
                    self.browser.close_browser()
                    time.sleep(2)
                except:
                    # 강제 종료
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            return False
    
    def repeat_cycle(self, repeat_count=1, search_query=None, airplane_duration=5, take_screenshot=False, test_mode=False, interval_seconds=10, keep_browser_open=False):
        """지정된 횟수만큼 사이클 반복 실행"""
        print(f"\n{'='*60}")
        mode_text = "테스트 모드" if test_mode else "일반 모드"
        browser_mode = "브라우저 유지" if keep_browser_open else "매번 새 브라우저"
        print(f"🔄 {mode_text} - {repeat_count}회 반복 실행 시작 ({browser_mode})")
        print(f"⏰ 사이클간 간격: {interval_seconds}초")
        print(f"{'='*60}")
        
        success_count = 0
        failed_count = 0
        browser_instance = None
        
        try:
            # keep_browser_open이 True인 경우 브라우저를 한 번만 생성
            if keep_browser_open:
                print("🌐 브라우저 인스턴스 생성 중...")
                browser_instance = AutoSeleniumBrowser(headless=test_mode)
                print("✅ 브라우저가 열렸습니다. 모든 사이클에서 재사용됩니다.")
            
            for i in range(repeat_count):
                current_cycle = i + 1
                print(f"\n📊 {current_cycle}/{repeat_count} 사이클 시작")
                
                success = self.single_cycle(
                    search_query=search_query,
                    airplane_duration=airplane_duration,
                    take_screenshot=take_screenshot,
                    test_mode=test_mode,
                    browser_instance=browser_instance,
                    cycle_number=current_cycle
                )
                
                if success:
                    success_count += 1
                    print(f"✅ {current_cycle}번째 사이클 성공")
                else:
                    failed_count += 1
                    print(f"❌ {current_cycle}번째 사이클 실패")
                
                # 마지막 사이클이 아닌 경우 대기
                if current_cycle < repeat_count:
                    print(f"⏰ {interval_seconds}초 후 다음 사이클 시작...")
                    time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 반복 실행 중 오류: {e}")
        finally:
            # 브라우저 정리
            if keep_browser_open and browser_instance:
                try:
                    print("🔄 브라우저 최종 종료 중...")
                    time.sleep(1)
                    browser_instance.close_browser()
                    print("🚪 브라우저 최종 종료")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ 브라우저 종료 중 오류: {e}")
                    # 강제 종료
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            
            # 결과 요약
            print(f"\n{'='*60}")
            print(f"📈 반복 실행 결과 요약")
            print(f"{'='*60}")
            print(f"🎯 요청된 횟수: {repeat_count}")
            print(f"✅ 성공한 횟수: {success_count}")
            print(f"❌ 실패한 횟수: {failed_count}")
            print(f"📊 성공률: {(success_count/max(success_count+failed_count, 1)*100):.1f}%")
            
            if test_mode:
                print(f"🧪 테스트 모드로 실행됨 (안드로이드 기능 제외)")
            
            return success_count, failed_count
    
    def continuous_mode(self, interval_seconds=60, search_query=None, test_mode=False, keep_browser_open=False):
        """무제한 연속 실행 모드"""
        mode_text = "테스트 모드" if test_mode else "일반 모드"
        browser_mode = "브라우저 유지" if keep_browser_open else "매번 새 브라우저"
        print(f"\n🔄 {mode_text} - 무제한 연속 실행 시작 ({browser_mode}, 간격: {interval_seconds}초)")
        print("Ctrl+C를 눌러 중단할 수 있습니다.")
        
        self.running = True
        cycle_count = 0
        success_count = 0
        failed_count = 0
        browser_instance = None
        
        try:
            # keep_browser_open이 True인 경우 브라우저를 한 번만 생성
            if keep_browser_open:
                print("🌐 브라우저 인스턴스 생성 중...")
                browser_instance = AutoSeleniumBrowser(headless=test_mode)
                print("✅ 브라우저가 열렸습니다. 모든 사이클에서 재사용됩니다.")
            
            while self.running:
                cycle_count += 1
                print(f"\n📊 사이클 #{cycle_count} 시작")
                
                success = self.single_cycle(
                    search_query=search_query,
                    test_mode=test_mode,
                    browser_instance=browser_instance,
                    cycle_number=cycle_count
                )
                
                if success:
                    success_count += 1
                    print(f"✅ 사이클 #{cycle_count} 완료")
                else:
                    failed_count += 1
                    print(f"❌ 사이클 #{cycle_count} 실패")
                
                # 현재 상태 출력
                success_rate = (success_count / cycle_count * 100) if cycle_count > 0 else 0
                print(f"📈 현재 상태: {success_count}성공 / {failed_count}실패 / 성공률 {success_rate:.1f}%")
                
                if self.running:
                    print(f"⏰ {interval_seconds}초 대기 중... (다음 사이클: #{cycle_count + 1})")
                    time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        finally:
            self.running = False
            
            # 브라우저 정리
            if keep_browser_open and browser_instance:
                try:
                    print("🔄 브라우저 최종 종료 중...")
                    time.sleep(1)
                    browser_instance.close_browser()
                    print("🚪 브라우저 최종 종료")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ 브라우저 종료 중 오류: {e}")
                    # 강제 종료
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            
            # 최종 결과 요약
            print(f"\n{'='*60}")
            print(f"📈 연속 실행 최종 결과")
            print(f"{'='*60}")
            print(f"🎯 총 실행 횟수: {cycle_count}")
            print(f"✅ 성공한 횟수: {success_count}")
            print(f"❌ 실패한 횟수: {failed_count}")
            if cycle_count > 0:
                print(f"📊 성공률: {(success_count/cycle_count*100):.1f}%")

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

def cleanup_browser_processes():
    """남은 브라우저 프로세스 정리"""
    try:
        print("🧹 브라우저 프로세스 정리 중...")
        
        # Chrome 및 ChromeDriver 프로세스 종료
        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
        subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
        
        print("✅ 브라우저 프로세스 정리 완료")
        time.sleep(1)
        
    except Exception as e:
        print(f"⚠️ 프로세스 정리 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🤖 Selenium 자동 드라이버 설치 + 네이버 자동화")
    print("=" * 60)
    
    # 시작 전 기존 브라우저 프로세스 정리
    cleanup_browser_processes()
    
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
    
    try:
    
        while True:
            print("\n" + "="*60)
            print("🎯 Selenium 자동화 모드 선택")
            print("="*60)
            print("1. 단일 실행 (일반 모드)")
            print("2. 단일 실행 (테스트 모드 - 안드로이드 제외)")
            print("3. 반복 실행 (일반 모드)")
            print("4. 반복 실행 (테스트 모드 - 안드로이드 제외)")
            print("5. 무제한 연속 실행 (일반 모드)")
            print("6. 무제한 연속 실행 (테스트 모드 - 안드로이드 제외)")
            print("7. 비행기모드만 테스트")
            print("0. 종료")
            
            choice = input("\n선택하세요 (0-7): ").strip()
            
            if choice == "1":
                # 단일 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                    
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                controller.single_cycle(search_query, duration, take_screenshot, test_mode=False)
                
            elif choice == "2":
                # 단일 실행 (테스트 모드)
                print("\n🧪 테스트 모드 시작 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                
                print("\n📝 테스트 모드 정보:")
                print("- 안드로이드 비행기모드 기능은 실행되지 않습니다")
                if show_browser:
                    print("- 브라우저가 화면에 표시됩니다")
                else:
                    print("- 브라우저가 백그라운드에서 실행됩니다")
                
                controller.single_cycle(search_query, 0, take_screenshot, test_mode=not show_browser)
                
            elif choice == "3":
                # 반복 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                
                repeat_count = input("반복 횟수 입력 (기본값 3): ").strip()
                repeat_count = int(repeat_count) if repeat_count.isdigit() else 3
                
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                interval = input("사이클간 간격(초, 기본값 10): ").strip()
                interval = int(interval) if interval.isdigit() else 10
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                controller.repeat_cycle(
                    repeat_count=repeat_count,
                    search_query=search_query,
                    airplane_duration=duration,
                    take_screenshot=take_screenshot,
                    test_mode=False,
                    interval_seconds=interval,
                    keep_browser_open=keep_browser
                )
                
            elif choice == "4":
                # 반복 실행 (테스트 모드)
                print("\n🧪 테스트 모드 반복 실행 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                repeat_count = input("반복 횟수 입력 (기본값 3): ").strip()
                repeat_count = int(repeat_count) if repeat_count.isdigit() else 3
                
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                interval = input("사이클간 간격(초, 기본값 5): ").strip()
                interval = int(interval) if interval.isdigit() else 5
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                # 브라우저를 유지하는 경우 헤드리스 모드 선택
                if keep_browser:
                    show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                    test_mode_value = not show_browser  # 화면에 표시하면 headless=False
                else:
                    test_mode_value = True  # 매번 새로 시작하면 기본적으로 헤드리스
                
                controller.repeat_cycle(
                    repeat_count=repeat_count,
                    search_query=search_query,
                    airplane_duration=0,
                    take_screenshot=take_screenshot,
                    test_mode=test_mode_value,
                    interval_seconds=interval,
                    keep_browser_open=keep_browser
                )
                
            elif choice == "5":
                # 무제한 연속 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                    
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                interval = input("실행 간격(초, 기본값 60): ").strip()
                interval = int(interval) if interval.isdigit() else 60
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                controller.continuous_mode(interval, search_query, test_mode=False, keep_browser_open=keep_browser)
                
            elif choice == "6":
                # 무제한 연속 실행 (테스트 모드)
                print("\n🧪 테스트 모드 무제한 연속 실행 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                search_query = input("검색어 입력 (없으면 엔터): ").strip()
                search_query = search_query if search_query else None
                
                interval = input("실행 간격(초, 기본값 30): ").strip()
                interval = int(interval) if interval.isdigit() else 30
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                if keep_browser:
                    show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                    test_mode_value = not show_browser
                else:
                    test_mode_value = True
                
                print("📝 테스트 모드로 실행됩니다.")
                
                controller.continuous_mode(interval, search_query, test_mode=test_mode_value, keep_browser_open=keep_browser)
                
            elif choice == "7":
                # 비행기모드만 테스트
                if not controller.android.check_device_connection():
                    print("\n❌ 안드로이드 디바이스가 연결되지 않았습니다.")
                    continue
                    
                repeat_count = input("반복 횟수 입력 (기본값 1): ").strip()
                repeat_count = int(repeat_count) if repeat_count.isdigit() else 1
                
                duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                interval = input("사이클간 간격(초, 기본값 10): ").strip()
                interval = int(interval) if interval.isdigit() else 10
                
                success_count = 0
                for i in range(repeat_count):
                    print(f"\n📱 {i+1}/{repeat_count} 비행기모드 테스트")
                    if controller.android.airplane_mode_cycle(duration):
                        success_count += 1
                    
                    if i < repeat_count - 1:  # 마지막이 아니면 대기
                        print(f"⏰ {interval}초 후 다음 테스트...")
                        time.sleep(interval)
                
                print(f"\n📊 비행기모드 테스트 결과: {success_count}/{repeat_count} 성공")
                
            elif choice == "0":
                print("👋 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 올바른 번호를 선택해주세요.")
        
    except KeyboardInterrupt:
        print("\n🛑 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 오류: {e}")
    finally:
        # 프로그램 종료 시 모든 브라우저 프로세스 정리
        print("\n🧹 프로그램 종료 - 브라우저 프로세스 정리 중...")
        cleanup_browser_processes()
        print("👋 프로그램이 완전히 종료되었습니다.")

if __name__ == "__main__":
    main()