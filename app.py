import os
from dotenv import load_dotenv

# TODO: src/graph.py 구성을 완료하면 아래 주석을 해제
# from src.graph import run_graph

def main():
    load_dotenv()

    print("=" * 50)
    print(" 🤖 Mystic RAG QA 챗봇 프로토타입 CLI ")
    print("=" * 50)
    print("질문을 입력하세요. (종료하려면 'exit' 또는 'q' 입력)\n")

    while True:
        try:
            user_input = input("사용자: ")
            
            # 종료 조건
            if user_input.lower() in ['exit', 'q']:
                print("\n챗봇을 종료합니다. 감사합니다!")
                break
                
            # 빈 입력 방지
            if not user_input.strip():
                continue

            # ----------------------------------------------------
            # 실제 연결 로직 (코드 완성하면 활성화)
            # ----------------------------------------------------
            # result = run_graph(user_input)
            # print(f"\n챗봇: {result.get('answer', '답변을 생성하지 못했습니다.')}\n")
            
            print(f"\n챗봇: '{user_input}'에 대한 답변입니다. (현재 모듈 통합 대기 중)\n")

        except KeyboardInterrupt:
            print("\n\n강제 종료되었습니다.")
            break
        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}\n")

if __name__ == "__main__":
    main()