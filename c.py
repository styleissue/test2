#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 인간형 브라우저 자동화 시스템
- GPT API 연동으로 시나리오 생성
- 인간과 같은 스크롤, 클릭, 타이핑 패턴
- 무작위 페이지 탐색 및 상호작용
- 안드로이드 비행기모드 제어

OpenAI API 키는 여러 방법으로 설정할 수 있습니다! 🔑
🔧 API 키 설정 방법:
1. 환경변수로 설정 (권장)
Windows:
cmdset OPENAI_API_KEY=your-api-key-here
Mac/Linux:
bashexport OPENAI_API_KEY="your-api-key-here"

"""

import subprocess
import time
import os
import threading
import random
import json
import math
from typing import List, Dict, Tuple, Optional
import requests

# 자동 드라이버 설치를 위한 라이브러리들
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    print("✅ Selenium과 webdriver-manager가 설치되어 있습니다.")
except ImportError as e:
    print("❌ 필요한 라이브러리가 설치되지 않았습니다.")
    print("설치 명령어:")
    print("pip install selenium webdriver-manager requests")
    SELENIUM_AVAILABLE = False

class GPTScenarioGenerator:
    """GPT API를 사용한 시나리오 생성기"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
            print("환경변수 OPENAI_API_KEY를 설정하거나 직접 입력해주세요.")
    
    def generate_browsing_scenario(self, context: str = "") -> Dict:
        """브라우징 시나리오 생성"""
        if not self.api_key:
            print("🔄 API 키가 없으므로 기본 시나리오를 사용합니다.")
            return self.get_fallback_scenario()
            
        prompt = f"""
당신은 자연스러운 웹 브라우징 행동을 생성하는 AI입니다.
현재 상황: {context}

다음과 같은 JSON 형식으로 자연스러운 브라우징 시나리오를 생성해주세요:

{{
    "main_action": "검색 또는 특정 사이트 방문",
    "search_queries": ["검색어1", "검색어2", "검색어3"],
    "interaction_pattern": {{
        "scroll_behavior": "slow/medium/fast/random",
        "reading_time": 5,
        "click_probability": 0.3,
        "back_probability": 0.2
    }},
    "navigation_sequence": [
        "네이버 메인 접속",
        "검색어 입력",
        "검색 결과 확인",
        "특정 링크 클릭",
        "페이지 스크롤",
        "뒤로가기 또는 새 검색"
    ],
    "human_delays": {{
        "typing_delay": 0.2,
        "reading_delay": 3,
        "decision_delay": 2
    }}
}}

일반적인 한국인의 웹 사용 패턴을 반영해주세요.
검색어는 시사, 날씨, 쇼핑, 연예, 게임 등 다양한 주제로 만들어주세요.
"""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "당신은 자연스러운 웹 브라우징 패턴을 생성하는 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.8
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # JSON 추출 시도
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_str = content[start:end]
                    scenario = json.loads(json_str)
                    print("🤖 GPT가 새로운 시나리오를 생성했습니다!")
                    return scenario
                except (json.JSONDecodeError, ValueError):
                    print("⚠️ GPT 응답을 JSON으로 파싱할 수 없습니다. 기본 시나리오를 사용합니다.")
                    return self.get_fallback_scenario()
            else:
                print(f"⚠️ GPT API 호출 실패: {response.status_code}")
                return self.get_fallback_scenario()
                
        except Exception as e:
            print(f"⚠️ GPT API 호출 중 오류: {e}")
            return self.get_fallback_scenario()
    
    def get_fallback_scenario(self) -> Dict:
        """API 실패 시 사용할 기본 시나리오"""
        scenarios = [
            {
                "main_action": "일반적인 검색",
                "search_queries": ["오늘 날씨", "최신 뉴스", "맛집 추천"],
                "interaction_pattern": {
                    "scroll_behavior": "medium",
                    "reading_time": random.randint(3, 8),
                    "click_probability": 0.3,
                    "back_probability": 0.2
                },
                "navigation_sequence": [
                    "네이버 메인 접속",
                    "검색어 입력",
                    "검색 결과 확인",
                    "페이지 스크롤",
                    "새 검색 또는 종료"
                ],
                "human_delays": {
                    "typing_delay": random.uniform(0.1, 0.3),
                    "reading_delay": random.randint(2, 5),
                    "decision_delay": random.uniform(1, 3)
                }
            },
            {
                "main_action": "쇼핑 탐색",
                "search_queries": ["겨울 패딩", "스마트폰 추천", "생활용품"],
                "interaction_pattern": {
                    "scroll_behavior": "slow",
                    "reading_time": random.randint(5, 12),
                    "click_probability": 0.4,
                    "back_probability": 0.3
                },
                "navigation_sequence": [
                    "네이버 메인 접속",
                    "쇼핑 검색",
                    "상품 확인",
                    "상세 페이지 방문",
                    "가격 비교",
                    "뒤로가기"
                ],
                "human_delays": {
                    "typing_delay": random.uniform(0.15, 0.4),
                    "reading_delay": random.randint(3, 8),
                    "decision_delay": random.uniform(2, 5)
                }
            },
            {
                "main_action": "뉴스 및 정보 확인",
                "search_queries": ["코로나 현황", "주식 시세", "연예 뉴스"],
                "interaction_pattern": {
                    "scroll_behavior": "fast",
                    "reading_time": random.randint(4, 9),
                    "click_probability": 0.5,
                    "back_probability": 0.1
                },
                "navigation_sequence": [
                    "네이버 메인 접속",
                    "뉴스 섹션 방문",
                    "기사 클릭",
                    "댓글 확인",
                    "관련 기사 클릭",
                    "메인으로 복귀"
                ],
                "human_delays": {
                    "typing_delay": random.uniform(0.08, 0.25),
                    "reading_delay": random.randint(2, 6),
                    "decision_delay": random.uniform(0.5, 2)
                }
            },
            {
                "main_action": "여행 정보 검색",
                "search_queries": ["제주도 여행", "부산 맛집", "호텔 예약"],
                "interaction_pattern": {
                    "scroll_behavior": "random",
                    "reading_time": random.randint(6, 15),
                    "click_probability": 0.6,
                    "back_probability": 0.4
                },
                "navigation_sequence": [
                    "네이버 메인 접속",
                    "여행 검색",
                    "블로그 후기 확인",
                    "지도 확인",
                    "예약 사이트 방문",
                    "다른 지역 검색"
                ],
                "human_delays": {
                    "typing_delay": random.uniform(0.2, 0.5),
                    "reading_delay": random.randint(4, 10),
                    "decision_delay": random.uniform(2, 6)
                }
            }
        ]
        return random.choice(scenarios)

class HumanLikeActions:
    """인간과 같은 행동 패턴을 구현하는 클래스"""
    
    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)
    
    def human_type(self, element, text: str, typing_delay: float = 0.2):
        """인간과 같은 타이핑"""
        element.clear()
        
        for char in text:
            # 가끔 실수로 잘못 타이핑 후 지우기
            if random.random() < 0.05:  # 5% 확률로 실수
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
            
            element.send_keys(char)
            
            # 타이핑 속도 변화 (단어 사이 간격 더 길게)
            if char == ' ':
                time.sleep(random.uniform(typing_delay * 2, typing_delay * 4))
            else:
                time.sleep(random.uniform(typing_delay * 0.5, typing_delay * 1.5))
    
    def human_scroll(self, behavior: str = "medium", duration: float = 3.0):
        """인간과 같은 스크롤"""
        print(f"🖱️ {behavior} 스타일로 스크롤 중...")
        
        end_time = time.time() + duration
        
        if behavior == "slow":
            scroll_amounts = [-100, -200, -150, -300]
            base_delay = 0.8
        elif behavior == "fast":
            scroll_amounts = [-400, -500, -600, -800]
            base_delay = 0.2
        elif behavior == "random":
            scroll_amounts = [-50, -100, -200, -300, -400, -500]
            base_delay = random.uniform(0.1, 1.0)
        else:  # medium
            scroll_amounts = [-200, -300, -250, -400]
            base_delay = 0.4
        
        scroll_direction = 1  # 1: 아래로, -1: 위로
        
        while time.time() < end_time:
            # 가끔 스크롤 방향 바꾸기
            if random.random() < 0.1:
                scroll_direction *= -1
                print("📜 스크롤 방향 변경")
            
            scroll_amount = random.choice(scroll_amounts) * scroll_direction
            
            # 마우스 휠 스크롤 시뮬레이션
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # 가끔 스크롤 멈춤 (읽는 시간)
            if random.random() < 0.3:
                read_time = random.uniform(1, 3)
                print(f"📖 {read_time:.1f}초 간 읽기")
                time.sleep(read_time)
            
            time.sleep(random.uniform(base_delay * 0.5, base_delay * 1.5))
        
        # 마지막에 페이지 상단으로 돌아갈 확률
        if random.random() < 0.2:
            print("⬆️ 페이지 상단으로 이동")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
    
    def human_click(self, element, click_delay: float = 0.5):
        """인간과 같은 클릭"""
        try:
            # 요소로 마우스 이동 (약간의 지연과 함께)
            self.actions.move_to_element(element).perform()
            time.sleep(random.uniform(0.2, 0.8))
            
            # 가끔 요소 주변을 클릭하는 실수
            if random.random() < 0.05:
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                self.actions.move_to_element_with_offset(element, offset_x, offset_y).perform()
            
            # 클릭 전 짧은 대기
            time.sleep(random.uniform(0.1, click_delay))
            
            element.click()
            print("🖱️ 요소 클릭 완료")
            
            # 클릭 후 대기
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"🖱️ 클릭 실패: {e}")
    
    def random_mouse_movement(self):
        """무작위 마우스 움직임"""
        try:
            window_size = self.driver.get_window_size()
            width, height = window_size['width'], window_size['height']
            
            # 무작위 위치로 마우스 이동
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            
            self.actions.move_by_offset(x - width//2, y - height//2).perform()
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"🖱️ 마우스 움직임 실패: {e}")
    
    def simulate_reading(self, min_time: float = 2.0, max_time: float = 10.0):
        """읽기 시뮬레이션"""
        read_time = random.uniform(min_time, max_time)
        print(f"📚 {read_time:.1f}초 간 페이지 읽기 시뮬레이션")
        
        # 읽기 중간에 가끔 스크롤
        intervals = random.randint(2, 4)
        for i in range(intervals):
            time.sleep(read_time / intervals)
            if random.random() < 0.4:  # 40% 확률로 작은 스크롤
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(-100, 200)});")

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
        
        if self.set_airplane_mode(True):
            print(f"⏰ {duration}초 대기 중...")
            time.sleep(duration)
            
            if self.set_airplane_mode(False):
                print("✅ 비행기모드 사이클이 완료되었습니다.")
                return True
        
        return False

class AIBrowserAutomation:
    """AI 기반 브라우저 자동화"""
    
    def __init__(self, gpt_api_key: str = None, headless: bool = False):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium과 webdriver-manager가 설치되지 않았습니다.")
        
        self.gpt_generator = GPTScenarioGenerator(gpt_api_key)
        self.driver = None
        self.human_actions = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            print("🔄 ChromeDriver 자동 설치 중...")
            
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
            
            # 더 자연스러운 User-Agent
            user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # ChromeDriver 자동 다운로드 및 설치
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            
            # WebDriver 초기화
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # 인간형 액션 클래스 초기화
            self.human_actions = HumanLikeActions(self.driver)
            
            print("✅ AI 기반 WebDriver가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            print(f"❌ WebDriver 초기화 실패: {e}")
            raise
    
    def execute_ai_scenario(self, context: str = ""):
        """AI 생성 시나리오 실행"""
        print("\n🤖 AI 시나리오 생성 중...")
        scenario = self.gpt_generator.generate_browsing_scenario(context)
        
        print("📋 생성된 시나리오:")
        print(f"   주요 액션: {scenario.get('main_action', '정보 없음')}")
        print(f"   검색어: {scenario.get('search_queries', [])}")
        print(f"   스크롤 패턴: {scenario.get('interaction_pattern', {}).get('scroll_behavior', 'medium')}")
        
        return self.execute_scenario(scenario)
    
    def execute_scenario(self, scenario: Dict) -> bool:
        """시나리오 실행"""
        try:
            # 1. 네이버 메인 페이지 접속
            print("\n🌐 네이버 메인 페이지 접속 중...")
            self.driver.get("https://www.naver.com")
            
            # 페이지 로드 대기
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"✅ 네이버 접속 성공: {self.driver.title}")
            
            # 초기 읽기 시뮬레이션
            human_delays = scenario.get('human_delays', {})
            initial_reading = human_delays.get('reading_delay', random.randint(2, 5))
            self.human_actions.simulate_reading(initial_reading, initial_reading + 3)
            
            # 2. 검색어 선택 및 검색
            search_queries = scenario.get('search_queries', ['오늘 날씨'])
            selected_query = random.choice(search_queries)
            
            print(f"🔍 선택된 검색어: '{selected_query}'")
            
            if self.perform_search(selected_query, scenario):
                # 3. 검색 결과 페이지에서 인간형 행동
                self.perform_human_browsing(scenario)
                
                # 4. 추가 탐색 (확률적)
                if random.random() < 0.4:  # 40% 확률로 추가 탐색
                    self.perform_additional_exploration(scenario)
                
                return True
            else:
                print("❌ 검색 실패")
                return False
                
        except Exception as e:
            print(f"❌ 시나리오 실행 중 오류: {e}")
            return False
    
    def perform_search(self, query: str, scenario: Dict) -> bool:
        """검색 수행"""
        try:
            typing_delay = scenario.get('human_delays', {}).get('typing_delay', 0.2)
            
            # 검색창 찾기
            search_selectors = [
                (By.ID, "query"),
                (By.NAME, "query"),
                (By.CSS_SELECTOR, "input[placeholder*='검색']"),
                (By.CSS_SELECTOR, ".search_input"),
                (By.CSS_SELECTOR, "#nx_query")
            ]
            
            search_box = None
            for by, selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except:
                    continue
            
            if not search_box:
                print("❌ 검색창을 찾을 수 없습니다.")
                return False
            
            # 검색창 클릭 및 포커스
            self.human_actions.human_click(search_box)
            
            # 결정 지연 시뮬레이션
            decision_delay = scenario.get('human_delays', {}).get('decision_delay', 1)
            time.sleep(random.uniform(decision_delay * 0.5, decision_delay))
            
            # 인간형 타이핑
            self.human_actions.human_type(search_box, query, typing_delay)
            
            # 검색 실행 (Enter 키 또는 버튼 클릭)
            if random.random() < 0.7:  # 70% 확률로 Enter 키 사용
                search_box.send_keys(Keys.RETURN)
                print("⌨️ Enter 키로 검색 실행")
            else:
                # 검색 버튼 찾기 및 클릭
                search_buttons = [
                    (By.CLASS_NAME, "btn_search"),
                    (By.CSS_SELECTOR, ".search_btn"),
                    (By.CSS_SELECTOR, "button[type='submit']"),
                    (By.ID, "search_btn")
                ]
                
                for by, selector in search_buttons:
                    try:
                        search_button = self.driver.find_element(by, selector)
                        self.human_actions.human_click(search_button)
                        print("🖱️ 검색 버튼 클릭")
                        break
                    except:
                        continue
            
            # 검색 결과 페이지 로드 대기
            WebDriverWait(self.driver, 10).until(
                lambda driver: "search.naver.com" in driver.current_url or len(driver.find_elements(By.CSS_SELECTOR, ".lst_type")) > 0
            )
            
            print(f"✅ '{query}' 검색 완료")
            return True
            
        except Exception as e:
            print(f"🔍 검색 실패: {e}")
            return False
    
    def perform_human_browsing(self, scenario: Dict):
        """인간형 브라우징 행동"""
        interaction_pattern = scenario.get('interaction_pattern', {})
        
        # 스크롤 행동
        scroll_behavior = interaction_pattern.get('scroll_behavior', 'medium')
        reading_time = interaction_pattern.get('reading_time', 5)
        
        self.human_actions.human_scroll(scroll_behavior, reading_time)
        
        # 링크 클릭 확률
        click_probability = interaction_pattern.get('click_probability', 0.3)
        
        if random.random() < click_probability:
            self.try_click_search_result()
        
        # 무작위 마우스 움직임
        if random.random() < 0.3:
            self.human_actions.random_mouse_movement()
        
        # 뒤로가기 확률
        back_probability = interaction_pattern.get('back_probability', 0.2)
        if random.random() < back_probability:
            print("⬅️ 뒤로가기")
            self.driver.back()
            time.sleep(random.uniform(1, 3))
    
    def try_click_search_result(self):
        """검색 결과 클릭 시도"""
        try:
            # 클릭 가능한 검색 결과 찾기
            result_selectors = [
                ".lst_type li a",
                ".search_result a",
                ".result_list a",
                ".api_subject_bx a"
            ]
            
            clickable_elements = []
            for selector in result_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                clickable_elements.extend(elements)
            
            if clickable_elements:
                # 화면에 보이는 요소만 필터링
                visible_elements = [elem for elem in clickable_elements if elem.is_displayed()]
                
                if visible_elements:
                    # 상위 몇 개 결과 중에서 선택 (더 자연스럽게)
                    top_results = visible_elements[:min(5, len(visible_elements))]
                    selected_element = random.choice(top_results)
                    
                    print("🖱️ 검색 결과 클릭 시도")
                    self.human_actions.human_click(selected_element)
                    
                    # 새 페이지 로딩 대기
                    time.sleep(random.uniform(2, 5))
                    
                    # 새 페이지에서 읽기 시뮬레이션
                    self.human_actions.simulate_reading(3, 8)
                    
                    return True
            
        except Exception as e:
            print(f"🖱️ 검색 결과 클릭 실패: {e}")
        
        return False
    
    def perform_additional_exploration(self, scenario: Dict):
        """추가 탐색 수행"""
        print("🔍 추가 탐색 시작...")
        
        exploration_actions = [
            self.try_related_search,
            self.explore_naver_sections,
            self.random_navigation
        ]
        
        selected_action = random.choice(exploration_actions)
        selected_action(scenario)
    
    def try_related_search(self, scenario: Dict):
        """연관 검색어로 새 검색"""
        try:
            # 연관 검색어 또는 새로운 검색어
            additional_queries = [
                "맛집 추천",
                "영화 예매",
                "온라인 쇼핑",
                "부동산 정보",
                "여행 정보",
                "요리 레시피",
                "운동 방법",
                "주식 정보",
                "날씨 예보",
                "교통 정보",
                "게임 공략",
                "아르바이트",
                "중고거래",
                "배달음식"
            ]
            
            new_query = random.choice(additional_queries)
            print(f"🔄 연관 검색: '{new_query}'")
            
            # 네이버 메인으로 이동하거나 새 검색창 사용
            if random.random() < 0.5:
                self.driver.get("https://www.naver.com")
                time.sleep(random.uniform(1, 3))
            
            return self.perform_search(new_query, scenario)
            
        except Exception as e:
            print(f"🔄 연관 검색 실패: {e}")
            return False
    
    def explore_naver_sections(self, scenario: Dict):
        """네이버 섹션 탐색"""
        try:
            print("📰 네이버 섹션 탐색 중...")
            
            # 네이버 주요 섹션들
            section_urls = [
                "https://news.naver.com",
                "https://sports.naver.com",
                "https://finance.naver.com",
                "https://shopping.naver.com",
                "https://map.naver.com",
                "https://weather.naver.com",
                "https://comic.naver.com",
                "https://cafe.naver.com"
            ]
            
            selected_url = random.choice(section_urls)
            print(f"🌐 {selected_url} 방문")
            
            self.driver.get(selected_url)
            time.sleep(random.uniform(2, 4))
            
            # 해당 섹션에서 인간형 브라우징
            self.human_actions.simulate_reading(3, 8)
            self.human_actions.human_scroll("medium", random.uniform(4, 8))
            
            # 기사나 콘텐츠 클릭 시도
            if random.random() < 0.4:
                self.try_click_content()
            
            return True
            
        except Exception as e:
            print(f"📰 섹션 탐색 실패: {e}")
            return False
    
    def try_click_content(self):
        """콘텐츠 클릭 시도"""
        try:
            # 다양한 콘텐츠 선택자
            content_selectors = [
                "a[href*='news']",
                ".news_tit",
                ".headline",
                ".item_title",
                ".link_txt",
                ".subject",
                "h3 a",
                "h4 a",
                ".tit",
                ".title"
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [elem for elem in elements if elem.is_displayed()]
                    
                    if visible_elements:
                        selected = random.choice(visible_elements[:3])  # 상위 3개 중 선택
                        print("📰 콘텐츠 클릭")
                        self.human_actions.human_click(selected)
                        
                        # 새 페이지에서 읽기
                        time.sleep(random.uniform(2, 4))
                        self.human_actions.simulate_reading(5, 12)
                        
                        # 스크롤로 기사 읽기 시뮬레이션
                        self.human_actions.human_scroll("slow", random.uniform(6, 10))
                        
                        return True
                except:
                    continue
            
        except Exception as e:
            print(f"📰 콘텐츠 클릭 실패: {e}")
        
        return False
    
    def random_navigation(self, scenario: Dict):
        """무작위 네비게이션"""
        try:
            print("🎲 무작위 네비게이션")
            
            actions = [
                lambda: self.driver.refresh(),
                lambda: self.driver.back(),
                lambda: self.driver.forward(),
                lambda: self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"),
                lambda: self.driver.execute_script("window.scrollTo(0, 0);")
            ]
            
            # 여러 액션 조합 실행
            num_actions = random.randint(1, 3)
            for _ in range(num_actions):
                action = random.choice(actions)
                try:
                    action()
                    time.sleep(random.uniform(1, 3))
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"🎲 무작위 네비게이션 실패: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """스크린샷 저장"""
        try:
            if not filename:
                filename = f"ai_browsing_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            print(f"📸 스크린샷 저장: {filename}")
            return filename
        except Exception as e:
            print(f"📸 스크린샷 실패: {e}")
            return None
    
    def get_page_analysis(self) -> Dict:
        """현재 페이지 분석"""
        try:
            analysis = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'page_height': self.driver.execute_script("return document.body.scrollHeight"),
                'viewport_height': self.driver.execute_script("return window.innerHeight"),
                'links_count': len(self.driver.find_elements(By.TAG_NAME, "a")),
                'images_count': len(self.driver.find_elements(By.TAG_NAME, "img")),
                'time': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("📊 페이지 분석:")
            for key, value in analysis.items():
                print(f"   {key}: {value}")
            
            return analysis
        except Exception as e:
            print(f"📊 페이지 분석 실패: {e}")
            return {}
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            try:
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                
                self.driver.quit()
                print("🚪 AI 브라우저가 완전히 종료되었습니다.")
                
                # 프로세스 정리
                try:
                    subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                    subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ 브라우저 종료 중 오류: {e}")
                try:
                    subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                    subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                    print("🔴 브라우저 프로세스 강제 종료")
                except:
                    pass
            finally:
                self.driver = None

class AdvancedAutomationController:
    """고급 자동화 컨트롤러"""
    
    def __init__(self, gpt_api_key: str = None):
        self.gpt_api_key = gpt_api_key
        self.android = AndroidAirplaneMode()
        self.ai_browser = None
        self.running = False
        self.session_stats = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'start_time': None,
            'scenarios_used': []
        }
    
    def check_prerequisites(self, test_mode: bool = False):
        """사전 요구사항 확인"""
        print("📋 사전 요구사항 확인 중...")
        
        # Selenium 확인
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium이 설치되지 않았습니다.")
            return False
        
        # GPT API 키 확인
        if not self.gpt_api_key and not os.getenv('OPENAI_API_KEY'):
            print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
            print("GPT 기능 없이 기본 시나리오로 실행됩니다.")
        
        # 안드로이드 확인 (테스트 모드가 아닌 경우)
        adb_ok = True
        if not test_mode:
            adb_ok = self.android.check_device_connection()
        else:
            print("🧪 테스트 모드: 안드로이드 디바이스 확인을 건너뜁니다.")
        
        # 브라우저 테스트
        try:
            print("🔧 AI 브라우저 초기화 테스트 중...")
            test_browser = AIBrowserAutomation(self.gpt_api_key, headless=True)
            test_browser.close_browser()
            print("✅ AI 브라우저 테스트 완료")
            return adb_ok if not test_mode else True
        except Exception as e:
            print(f"❌ AI 브라우저 테스트 실패: {e}")
            return False
    
    def single_ai_cycle(self, context: str = "", airplane_duration: int = 5, 
                       take_screenshot: bool = False, test_mode: bool = False, 
                       browser_instance=None, cycle_number: int = 1) -> bool:
        """단일 AI 사이클 실행"""
        print(f"\n{'='*60}")
        mode_text = "🧪 AI 테스트 모드" if test_mode else "🤖 AI 일반 모드"
        print(f"{mode_text} - 사이클 #{cycle_number} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        create_new_browser = browser_instance is None
        
        try:
            # 브라우저 초기화
            if create_new_browser:
                self.ai_browser = AIBrowserAutomation(self.gpt_api_key, headless=test_mode)
                print("🤖 새 AI 브라우저 인스턴스 생성")
            else:
                self.ai_browser = browser_instance
                print("🤖 기존 AI 브라우저 인스턴스 사용")
            
            # AI 시나리오 생성 및 실행
            scenario_context = f"{context} - 사이클 #{cycle_number}"
            success = self.ai_browser.execute_ai_scenario(scenario_context)
            
            if not success:
                print("❌ AI 시나리오 실행 실패")
                if create_new_browser:
                    self.ai_browser.close_browser()
                return False
            
            # 페이지 분석
            self.ai_browser.get_page_analysis()
            
            # 스크린샷 (선택사항)
            if take_screenshot:
                screenshot_name = f"ai_cycle_{cycle_number}_{int(time.time())}.png"
                self.ai_browser.take_screenshot(screenshot_name)
            
            # 브라우저 처리
            if create_new_browser:
                time.sleep(random.uniform(1, 3))
                self.ai_browser.close_browser()
                print("🚪 AI 브라우저 종료")
                time.sleep(2)
            else:
                print("🤖 AI 브라우저 유지 (다음 사이클에서 재사용)")
            
            # 비행기모드 사이클 (테스트 모드가 아닐 때만)
            if not test_mode:
                airplane_success = self.android.airplane_mode_cycle(airplane_duration)
                
                if airplane_success:
                    print("✅ 전체 AI 사이클 완료")
                    self.session_stats['successful_cycles'] += 1
                    return True
                else:
                    print("⚠️ 비행기모드 실패, AI 웹 접속은 성공")
                    self.session_stats['successful_cycles'] += 1
                    return True
            else:
                print("🧪 AI 테스트 모드 완료 - 안드로이드 기능 건너뜀")
                self.session_stats['successful_cycles'] += 1
                return True
                
        except Exception as e:
            print(f"❌ AI 사이클 실행 중 오류: {e}")
            self.session_stats['failed_cycles'] += 1
            
            if create_new_browser and self.ai_browser:
                try:
                    time.sleep(1)
                    self.ai_browser.close_browser()
                    time.sleep(2)
                except:
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            return False
        finally:
            self.session_stats['total_cycles'] += 1
    
    def repeat_ai_cycles(self, repeat_count: int = 1, context: str = "", 
                        airplane_duration: int = 5, take_screenshot: bool = False, 
                        test_mode: bool = False, interval_seconds: int = 10, 
                        keep_browser_open: bool = False):
        """AI 사이클 반복 실행"""
        print(f"\n{'='*60}")
        mode_text = "🧪 AI 테스트 모드" if test_mode else "🤖 AI 일반 모드"
        browser_mode = "브라우저 유지" if keep_browser_open else "매번 새 브라우저"
        print(f"🔄 {mode_text} - {repeat_count}회 반복 실행 시작 ({browser_mode})")
        print(f"⏰ 사이클간 간격: {interval_seconds}초")
        print(f"{'='*60}")
        
        self.session_stats['start_time'] = time.time()
        browser_instance = None
        
        try:
            if keep_browser_open:
                print("🤖 AI 브라우저 인스턴스 생성 중...")
                browser_instance = AIBrowserAutomation(self.gpt_api_key, headless=test_mode)
                print("✅ AI 브라우저가 열렸습니다. 모든 사이클에서 재사용됩니다.")
            
            for i in range(repeat_count):
                current_cycle = i + 1
                print(f"\n📊 {current_cycle}/{repeat_count} AI 사이클 시작")
                
                cycle_context = f"{context} - 반복 실행 {current_cycle}/{repeat_count}"
                
                success = self.single_ai_cycle(
                    context=cycle_context,
                    airplane_duration=airplane_duration,
                    take_screenshot=take_screenshot,
                    test_mode=test_mode,
                    browser_instance=browser_instance,
                    cycle_number=current_cycle
                )
                
                if success:
                    print(f"✅ {current_cycle}번째 AI 사이클 성공")
                else:
                    print(f"❌ {current_cycle}번째 AI 사이클 실패")
                
                # 마지막 사이클이 아닌 경우 대기
                if current_cycle < repeat_count:
                    print(f"⏰ {interval_seconds}초 후 다음 AI 사이클 시작...")
                    time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ AI 반복 실행 중 오류: {e}")
        finally:
            if keep_browser_open and browser_instance:
                try:
                    print("🔄 AI 브라우저 최종 종료 중...")
                    time.sleep(1)
                    browser_instance.close_browser()
                    print("🚪 AI 브라우저 최종 종료")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ AI 브라우저 종료 중 오류: {e}")
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            
            self.print_session_summary()
    
    def continuous_ai_mode(self, interval_seconds: int = 60, context: str = "", 
                          test_mode: bool = False, keep_browser_open: bool = False):
        """무제한 AI 연속 실행 모드"""
        mode_text = "🧪 AI 테스트 모드" if test_mode else "🤖 AI 일반 모드"
        browser_mode = "브라우저 유지" if keep_browser_open else "매번 새 브라우저"
        print(f"\n🔄 {mode_text} - 무제한 연속 실행 시작 ({browser_mode}, 간격: {interval_seconds}초)")
        print("Ctrl+C를 눌러 중단할 수 있습니다.")
        
        self.running = True
        self.session_stats['start_time'] = time.time()
        browser_instance = None
        
        try:
            if keep_browser_open:
                print("🤖 AI 브라우저 인스턴스 생성 중...")
                browser_instance = AIBrowserAutomation(self.gpt_api_key, headless=test_mode)
                print("✅ AI 브라우저가 열렸습니다. 모든 사이클에서 재사용됩니다.")
            
            cycle_count = 0
            
            while self.running:
                cycle_count += 1
                print(f"\n📊 AI 사이클 #{cycle_count} 시작")
                
                cycle_context = f"{context} - 연속 실행 사이클 #{cycle_count}"
                
                success = self.single_ai_cycle(
                    context=cycle_context,
                    test_mode=test_mode,
                    browser_instance=browser_instance,
                    cycle_number=cycle_count
                )
                
                if success:
                    print(f"✅ AI 사이클 #{cycle_count} 완료")
                else:
                    print(f"❌ AI 사이클 #{cycle_count} 실패")
                
                # 현재 상태 출력
                success_rate = (self.session_stats['successful_cycles'] / self.session_stats['total_cycles'] * 100) if self.session_stats['total_cycles'] > 0 else 0
                print(f"📈 현재 상태: {self.session_stats['successful_cycles']}성공 / {self.session_stats['failed_cycles']}실패 / 성공률 {success_rate:.1f}%")
                
                if self.running:
                    print(f"⏰ {interval_seconds}초 대기 중... (다음 AI 사이클: #{cycle_count + 1})")
                    time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        finally:
            self.running = False
            
            if keep_browser_open and browser_instance:
                try:
                    print("🔄 AI 브라우저 최종 종료 중...")
                    time.sleep(1)
                    browser_instance.close_browser()
                    print("🚪 AI 브라우저 최종 종료")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ AI 브라우저 종료 중 오류: {e}")
                    try:
                        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
                        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
                        print("🔴 브라우저 프로세스 강제 종료")
                    except:
                        pass
            
            self.print_session_summary()
    
    def print_session_summary(self):
        """세션 요약 출력"""
        print(f"\n{'='*60}")
        print(f"📈 AI 자동화 세션 결과 요약")
        print(f"{'='*60}")
        print(f"🎯 총 실행 횟수: {self.session_stats['total_cycles']}")
        print(f"✅ 성공한 횟수: {self.session_stats['successful_cycles']}")
        print(f"❌ 실패한 횟수: {self.session_stats['failed_cycles']}")
        
        if self.session_stats['total_cycles'] > 0:
            success_rate = (self.session_stats['successful_cycles'] / self.session_stats['total_cycles'] * 100)
            print(f"📊 성공률: {success_rate:.1f}%")
        
        if self.session_stats['start_time']:
            duration = time.time() - self.session_stats['start_time']
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"⏰ 총 실행 시간: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

def install_requirements():
    """필요한 라이브러리 자동 설치"""
    required_packages = [
        "selenium",
        "webdriver-manager",
        "requests"
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
        subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True)
        subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
        subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
        print("✅ 브라우저 프로세스 정리 완료")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ 프로세스 정리 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🤖 AI 기반 인간형 브라우저 자동화 시스템")
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
            print("pip install selenium webdriver-manager requests")
            return
    
    # OpenAI API 키 설정
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API 키 설정")
        print("환경변수에 OPENAI_API_KEY가 설정되지 않았습니다.")
        api_key = input("OpenAI API 키를 입력하세요 (없으면 엔터 - 기본 시나리오 사용): ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        else:
            print("⚠️ API 키 없이 기본 시나리오로 실행됩니다.")
    
    controller = AdvancedAutomationController(api_key)
    
    try:
        while True:
            print("\n" + "="*60)
            print("🤖 AI 기반 인간형 브라우저 자동화 모드 선택")
            print("="*60)
            print("1. 단일 AI 실행 (일반 모드)")
            print("2. 단일 AI 실행 (테스트 모드 - 안드로이드 제외)")
            print("3. 반복 AI 실행 (일반 모드)")
            print("4. 반복 AI 실행 (테스트 모드 - 안드로이드 제외)")
            print("5. 무제한 AI 연속 실행 (일반 모드)")
            print("6. 무제한 AI 연속 실행 (테스트 모드 - 안드로이드 제외)")
            print("7. 비행기모드만 테스트")
            print("8. AI 시나리오 미리보기")
            print("0. 종료")
            
            choice = input("\n선택하세요 (0-8): ").strip()
            
            if choice == "1":
                # 단일 AI 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                    
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                controller.single_ai_cycle(context, duration, take_screenshot, test_mode=False)
                
            elif choice == "2":
                # 단일 AI 실행 (테스트 모드)
                print("\n🧪 AI 테스트 모드 시작 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                
                print("\n📝 AI 테스트 모드 정보:")
                print("- AI가 인간형 브라우징 패턴을 생성합니다")
                print("- 안드로이드 비행기모드 기능은 실행되지 않습니다")
                if show_browser:
                    print("- 브라우저가 화면에 표시됩니다")
                
                controller.single_ai_cycle(context, 0, take_screenshot, test_mode=not show_browser)
                
            elif choice == "3":
                # 반복 AI 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                    
                repeat_count = input("반복 횟수 입력 (기본값 3): ").strip()
                repeat_count = int(repeat_count) if repeat_count.isdigit() else 3
                
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                duration = input("비행기모드 지속시간(초, 기본값 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                interval = input("사이클간 간격(초, 기본값 10): ").strip()
                interval = int(interval) if interval.isdigit() else 10
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                controller.repeat_ai_cycles(
                    repeat_count=repeat_count,
                    context=context,
                    airplane_duration=duration,
                    take_screenshot=take_screenshot,
                    test_mode=False,
                    interval_seconds=interval,
                    keep_browser_open=keep_browser
                )
                
            elif choice == "4":
                # 반복 AI 실행 (테스트 모드)
                print("\n🧪 AI 테스트 모드 반복 실행 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                repeat_count = input("반복 횟수 입력 (기본값 3): ").strip()
                repeat_count = int(repeat_count) if repeat_count.isdigit() else 3
                
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                interval = input("사이클간 간격(초, 기본값 5): ").strip()
                interval = int(interval) if interval.isdigit() else 5
                
                take_screenshot = input("스크린샷을 저장하시겠습니까? (y/n): ").lower() == 'y'
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                if keep_browser:
                    show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                    test_mode_value = not show_browser
                else:
                    test_mode_value = True
                
                controller.repeat_ai_cycles(
                    repeat_count=repeat_count,
                    context=context,
                    airplane_duration=0,
                    take_screenshot=take_screenshot,
                    test_mode=test_mode_value,
                    interval_seconds=interval,
                    keep_browser_open=keep_browser
                )
                
            elif choice == "5":
                # 무제한 AI 연속 실행 (일반 모드)
                if not controller.check_prerequisites(test_mode=False):
                    print("\n❌ 사전 요구사항을 만족하지 않습니다.")
                    continue
                    
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                interval = input("실행 간격(초, 기본값 60): ").strip()
                interval = int(interval) if interval.isdigit() else 60
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                controller.continuous_ai_mode(interval, context, test_mode=False, keep_browser_open=keep_browser)
                
            elif choice == "6":
                # 무제한 AI 연속 실행 (테스트 모드)
                print("\n🧪 AI 테스트 모드 무제한 연속 실행 (안드로이드 기능 제외)")
                
                if not controller.check_prerequisites(test_mode=True):
                    print("\n❌ 브라우저 요구사항을 만족하지 않습니다.")
                    continue
                
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                interval = input("실행 간격(초, 기본값 30): ").strip()
                interval = int(interval) if interval.isdigit() else 30
                
                keep_browser = input("브라우저를 유지하시겠습니까? (y=유지, n=매번 새로시작): ").lower() == 'y'
                
                if keep_browser:
                    show_browser = input("브라우저를 화면에 표시하시겠습니까? (y/n): ").lower() == 'y'
                    test_mode_value = not show_browser
                else:
                    test_mode_value = True
                
                print("📝 AI 테스트 모드로 실행됩니다.")
                
                controller.continuous_ai_mode(interval, context, test_mode=test_mode_value, keep_browser_open=keep_browser)
                
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
                    
                    if i < repeat_count - 1:
                        print(f"⏰ {interval}초 후 다음 테스트...")
                        time.sleep(interval)
                
                print(f"\n📊 비행기모드 테스트 결과: {success_count}/{repeat_count} 성공")
                
            elif choice == "8":
                # AI 시나리오 미리보기
                print("\n🔮 AI 시나리오 미리보기")
                
                context = input("시나리오 컨텍스트 입력 (예: 쇼핑 관심, 뉴스 확인 등, 없으면 엔터): ").strip()
                
                try:
                    generator = GPTScenarioGenerator(controller.gpt_api_key)
                    scenario = generator.generate_browsing_scenario(context)
                    
                    print("\n📋 생성된 AI 시나리오:")
                    print("="*50)
                    print(f"🎯 주요 액션: {scenario.get('main_action', '정보 없음')}")
                    print(f"🔍 검색어들: {', '.join(scenario.get('search_queries', []))}")
                    
                    interaction = scenario.get('interaction_pattern', {})
                    print(f"🖱️ 스크롤 패턴: {interaction.get('scroll_behavior', 'medium')}")
                    print(f"📖 읽기 시간: {interaction.get('reading_time', 5)}초")
                    print(f"🖱️ 클릭 확률: {interaction.get('click_probability', 0.3)*100:.0f}%")
                    print(f"⬅️ 뒤로가기 확률: {interaction.get('back_probability', 0.2)*100:.0f}%")
                    
                    print(f"\n🕐 타이밍 설정:")
                    delays = scenario.get('human_delays', {})
                    print(f"   ⌨️ 타이핑 간격: {delays.get('typing_delay', 0.2)}초")
                    print(f"   📚 읽기 지연: {delays.get('reading_delay', 3)}초")
                    print(f"   🤔 결정 지연: {delays.get('decision_delay', 2)}초")
                    
                    print(f"\n📝 네비게이션 순서:")
                    for i, step in enumerate(scenario.get('navigation_sequence', []), 1):
                        print(f"   {i}. {step}")
                    
                    print("="*50)
                    
                except Exception as e:
                    print(f"❌ AI 시나리오 생성 실패: {e}")
                    print("기본 시나리오가 사용됩니다.")
                
            elif choice == "0":
                print("👋 AI 자동화 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 올바른 번호를 선택해주세요.")
        
    except KeyboardInterrupt:
        print("\n🛑 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 오류: {e}")
    finally:
        print("\n🧹 프로그램 종료 - 브라우저 프로세스 정리 중...")
        cleanup_browser_processes()
        print("👋 AI 기반 자동화 프로그램이 완전히 종료되었습니다.")

if __name__ == "__main__":
    main()