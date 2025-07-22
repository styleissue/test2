import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoProcessor
from PIL import Image
import requests
from io import BytesIO
import base64

class KoreanBlossomVision:
    def __init__(self, model_name="Bllossom/llama-3.1-Korean-Bllossom-Vision-8B"):
        """
        한국어 Bllossom Vision 모델 초기화
        텍스트와 이미지를 모두 처리할 수 있는 멀티모달 모델
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🌸 한국어 Bllossom Vision 모델 로딩 중...")
        print(f"📱 사용 디바이스: {self.device}")
        
        self.load_model()
    
    def load_model(self):
        """모델과 토크나이저 로드"""
        try:
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 프로세서 로드 (이미지 처리용)
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 모델 로드 설정
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            }
            
            # GPU 메모리 최적화
            if torch.cuda.is_available():
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            
            # 모델 로드
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            print("✅ 모델 로딩 완료!")
            self.print_model_info()
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            raise
    
    def print_model_info(self):
        """모델 정보 출력"""
        param_count = sum(p.numel() for p in self.model.parameters())
        print(f"📊 모델 파라미터 수: {param_count:,}")
        print(f"🌸 특징: 한국어 특화 + 비전 기능")
    
    def load_image(self, image_source):
        """다양한 소스에서 이미지 로드"""
        if isinstance(image_source, str):
            if image_source.startswith(('http://', 'https://')):
                # URL에서 이미지 다운로드
                response = requests.get(image_source)
                image = Image.open(BytesIO(response.content))
            else:
                # 로컬 파일에서 이미지 로드
                image = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            # PIL Image 객체
            image = image_source
        else:
            raise ValueError("지원하지 않는 이미지 형식입니다.")
        
        # RGB로 변환 (필요한 경우)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def generate_text(self, prompt: str, max_length: int = 512, temperature: float = 0.7):
        """텍스트만 사용한 생성"""
        # Llama 3.1 한국어 채팅 포맷
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # 생성된 텍스트에서 프롬프트 부분 제거
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if formatted_prompt in response:
            response = response.replace(formatted_prompt, "").strip()
        
        return response
    
    def analyze_image(self, image_source, question: str = "이 이미지에 대해 자세히 설명해주세요."):
        """이미지 분석 및 질문 답변"""
        try:
            # 이미지 로드
            image = self.load_image(image_source)
            
            # 멀티모달 프롬프트 구성
            prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n<image>\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            # 이미지와 텍스트 처리
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            ).to(self.device)
            
            # 생성
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=1024,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 응답 디코딩
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 프롬프트 부분 제거
            if "<|start_header_id|>assistant<|end_header_id|>" in response:
                response = response.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
            
            return response
            
        except Exception as e:
            return f"이미지 분석 중 오류가 발생했습니다: {e}"
    
    def chat_with_image(self, image_source, conversation_history=None):
        """이미지와 함께 대화하기"""
        if conversation_history is None:
            conversation_history = []
        
        image = self.load_image(image_source)
        
        print("🖼️ 이미지가 로드되었습니다. 이미지에 대해 질문해보세요!")
        print("💡 예시: '이 이미지에서 무엇을 볼 수 있나요?', '이 사람의 표정은 어떤가요?'")
        print("⏹️ 'quit'을 입력하면 종료됩니다.\n")
        
        while True:
            user_input = input("👤 질문: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                break
            
            if not user_input:
                continue
            
            print("🤖 분석 중...", end="", flush=True)
            
            try:
                response = self.analyze_image(image, user_input)
                print(f"\r🌸 Bllossom: {response}\n")
                
                # 대화 히스토리에 추가
                conversation_history.append({"user": user_input, "assistant": response})
                
            except Exception as e:
                print(f"\r❌ 오류: {e}\n")
    
    def batch_image_analysis(self, image_list, questions=None):
        """여러 이미지 배치 분석"""
        if questions is None:
            questions = ["이 이미지에 대해 설명해주세요."] * len(image_list)
        
        if len(questions) == 1:
            questions = questions * len(image_list)
        
        results = []
        
        for i, (image_source, question) in enumerate(zip(image_list, questions), 1):
            print(f"🔄 이미지 분석 중 ({i}/{len(image_list)})...")
            
            try:
                result = self.analyze_image(image_source, question)
                results.append({
                    "image": image_source,
                    "question": question,
                    "analysis": result
                })
            except Exception as e:
                results.append({
                    "image": image_source,
                    "question": question,
                    "error": str(e)
                })
        
        return results
    
    def korean_conversation(self):
        """한국어 텍스트 대화"""
        print("🌸 한국어 Bllossom과 대화해보세요!")
        print("💡 이 모델은 한국어에 특별히 최적화되어 있습니다.")
        print("⏹️ 'quit'을 입력하면 종료됩니다.\n")
        
        while True:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                break
            
            if not user_input:
                continue
            
            print("🤖 생각 중...", end="", flush=True)
            
            try:
                response = self.generate_text(user_input)
                print(f"\r🌸 Bllossom: {response}\n")
            except Exception as e:
                print(f"\r❌ 오류: {e}\n")

# 사용 예시 및 테스트 코드
def main():
    """메인 실행 함수"""
    print("🌸 한국어 Bllossom Vision 모델 테스트")
    print("=" * 40)
    
    try:
        # 모델 초기화
        bllossom = KoreanBlossomVision()
        
        print("\n🎯 사용 방법을 선택하세요:")
        print("1. 한국어 텍스트 대화")
        print("2. 이미지 분석 (URL 또는 파일)")
        print("3. 이미지와 대화하기")
        print("4. 배치 이미지 분석")
        print("5. 간단한 테스트")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == "1":
            bllossom.korean_conversation()
        
        elif choice == "2":
            image_path = input("이미지 URL 또는 파일 경로를 입력하세요: ").strip()
            question = input("질문을 입력하세요 (엔터로 기본 질문): ").strip()
            
            if not question:
                question = "이 이미지에 대해 자세히 설명해주세요."
            
            print("\n🔄 이미지 분석 중...")
            result = bllossom.analyze_image(image_path, question)
            print(f"\n🌸 분석 결과:\n{result}")
        
        elif choice == "3":
            image_path = input("이미지 URL 또는 파일 경로를 입력하세요: ").strip()
            bllossom.chat_with_image(image_path)
        
        elif choice == "4":
            print("배치 분석을 위해 이미지 URL들을 입력하세요 (빈 줄로 종료):")
            images = []
            while True:
                img_url = input(f"이미지 {len(images)+1}: ").strip()
                if not img_url:
                    break
                images.append(img_url)
            
            if images:
                results = bllossom.batch_image_analysis(images)
                print("\n📋 배치 분석 결과:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. 이미지: {result['image']}")
                    if 'analysis' in result:
                        print(f"   분석: {result['analysis'][:100]}...")
                    else:
                        print(f"   오류: {result['error']}")
        
        elif choice == "5":
            # 간단한 텍스트 테스트
            print("\n🧪 간단한 한국어 테스트:")
            test_prompt = "안녕하세요! 한국의 전통 음식에 대해 설명해주세요."
            result = bllossom.generate_text(test_prompt)
            print(f"질문: {test_prompt}")
            print(f"답변: {result}")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 프로그램을 중단합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")

# 샘플 이미지 URL들 (테스트용)
SAMPLE_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png"
]

# 특화 기능들
def korean_cooking_assistant():
    """한국 요리 도우미"""
    bllossom = KoreanBlossomVision()
    
    print("🍳 한국 요리 도우미입니다!")
    print("음식 사진을 보여주시면 레시피나 요리법을 알려드려요.")
    
    while True:
        image_path = input("\n음식 사진 URL을 입력하세요 (quit으로 종료): ").strip()
        if image_path.lower() == 'quit':
            break
        
        try:
            result = bllossom.analyze_image(
                image_path, 
                "이 음식의 이름과 만드는 방법을 한국어로 자세히 설명해주세요."
            )
            print(f"\n🌸 요리 분석:\n{result}")
        except Exception as e:
            print(f"❌ 분석 오류: {e}")

def document_reader():
    """문서 이미지 읽기"""
    bllossom = KoreanBlossomVision()
    
    print("📄 문서 이미지 읽기 도구입니다!")
    print("문서나 텍스트가 포함된 이미지를 분석해드려요.")
    
    while True:
        image_path = input("\n문서 이미지 URL을 입력하세요 (quit으로 종료): ").strip()
        if image_path.lower() == 'quit':
            break
        
        try:
            result = bllossom.analyze_image(
                image_path,
                "이 이미지에 있는 텍스트를 모두 읽어서 한국어로 정리해주세요."
            )
            print(f"\n📝 문서 내용:\n{result}")
        except Exception as e:
            print(f"❌ 읽기 오류: {e}")

if __name__ == "__main__":
    main()
    
    # 추가 기능 테스트
    print("\n🌸 추가 기능 테스트:")
    korean_cooking_assistant()
    document_reader()
    
    print("\n🌸 프로그램을 종료합니다. 감사합니다!")