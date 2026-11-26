"""Python, Git, Docker 학습 내용을 복습하는 터미널 퀴즈.
퀴즈와 최고 기록은 JSON 파일에 보관한다."""

import json
import os
import sys
import random


class Quiz:
    """문제 한 개를 만들고 해당 문제의 답을 확인한다."""

    def __init__(self, question: str, choices: list[str], answer: int):
        self.question = question
        self.choices = choices
        self.answer = answer  # 보기 번호는 1번부터 4번까지 사용

    def display(self, index: int = None) -> None:
        """문제 번호와 보기 목록을 화면에 보여 준다."""
        prefix = f"[문제 {index}] " if index is not None else "[문제] "
        print(f"\n{prefix}{self.question}")
        for idx, choice in enumerate(self.choices, start=1):
            print(f"  {idx}. {choice}")

    def is_correct(self, user_answer: int) -> bool:
        """입력한 번호를 저장된 정답 번호와 비교한다."""
        return self.answer == user_answer

    def to_dict(self) -> dict:
        """파일에 기록할 수 있도록 문제 정보를 딕셔너리로 정리한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """파일에서 읽은 문제 정보가 올바른지 검사한 뒤 객체로 만든다."""
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제 형식 오류")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지 형식 오류")
        if not all(isinstance(choice, str) and choice.strip() for choice in choices):
            raise ValueError("선택지 내용 오류")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호 오류")
        return cls(question, choices, answer)


class QuizGame:
    """여러 문제를 관리하며 메뉴 선택에 따라 게임을 진행한다."""

    def __init__(self, filepath: str = "state.json"):
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
        self.quizzes: list[Quiz] = []
        self.best_score: int = 0
        self.load_data()

    def get_default_quizzes(self) -> list[Quiz]:
        """처음 시작할 때 사용할 개발 기초 문제를 준비한다."""
        return [
            # Python 문법 문제
            Quiz(
                question="[파이썬] 문자열을 정수로 변환하는 함수는?",
                choices=["str()", "int()", "list()", "bool()"],
                answer=2,
            ),
            Quiz(
                question="[파이썬] 조건이 참인 동안 반복하는 문법은?",
                choices=["if", "def", "while", "class"],
                answer=3,
            ),

            # Git 명령어 문제
            Quiz(
                question="[Git] 새로운 로컬 Git 저장소를 초기화하는 명령어는?",
                choices=["git init", "git push", "git pull", "git log"],
                answer=1,
            ),
            Quiz(
                question="[Git] 스테이징된 변경 사항을 기록하는 명령어는?",
                choices=["git clone", "git status", "git checkout", "git commit"],
                answer=4,
            ),

            # Docker 사용법 문제
            Quiz(
                question="[Docker] 실행 중인 컨테이너 목록을 확인하는 명령어는?",
                choices=["docker build", "docker run", "docker ps", "docker stop"],
                answer=3,
            ),
            Quiz(
                question="[Docker] 이미지를 기반으로 새 컨테이너를 생성하고 실행하는 명령어는?",
                choices=["docker images", "docker run", "docker logs", "docker rm"],
                answer=2,
            ),
        ]

    def load_data(self) -> None:
        """이전에 저장한 기록을 읽는다. 읽을 수 없다면 초기 문제로 시작한다."""
        if not os.path.exists(self.filepath):
            print("데이터 파일(state.json)이 없어 기본 퀴즈 데이터를 생성합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.save_data()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_quizzes = data["quizzes"]
                if not isinstance(raw_quizzes, list):
                    raise ValueError("퀴즈 목록 형식 오류")
                self.quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
                self.best_score = data["best_score"]
                if type(self.best_score) is not int or not 0 <= self.best_score <= 100:
                    raise ValueError("점수 형식 오류")


            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")

        except (ValueError, KeyError, TypeError, OSError) as e:
            print(f"데이터 파일이 손상되었거나 읽을 수 없습니다 ({e}). 기본 데이터로 복구합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            self.save_data()

    def save_data(self) -> None:
        """현재 문제 목록과 최고 기록을 JSON 파일에 기록한다."""
        try:
            data = {
                "quizzes": [quiz.to_dict() for quiz in self.quizzes],
                "best_score": self.best_score,
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"데이터 저장 중 오류가 발생했습니다: {e}")

    # 입력값을 확인하는 공통 기능
    def prompt_int(self, prompt_text: str, min_val: int, max_val: int) -> int:
        """숫자를 올바르게 입력할 때까지 다시 질문한다.
        공백, 빈 입력, 숫자가 아닌 값, 지정 범위를 벗어난 값을 확인한다."""
        while True:
            raw_input = input(prompt_text).strip()
            if not raw_input:
                print("빈 입력입니다. 값을 입력해주세요.")
                continue

            try:
                val = int(raw_input)
            except ValueError:
                print(f"숫자가 아닙니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue

            if val < min_val or val > max_val:
                print(f"허용 범위 밖입니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                continue

            return val

    def prompt_text(self, prompt_text: str) -> str:
        """내용이 없는 입력은 받지 않고 다시 입력하도록 한다."""
        while True:
            val = input(prompt_text).strip()
            if not val:
                print("필수 입력 항목입니다. 내용을 입력해주세요.")
                continue
            return val

    # 메뉴에서 선택할 수 있는 기능
    def display_menu(self) -> None:
        """사용할 수 있는 기능과 메뉴 번호를 안내한다."""
        print("\n" + "=" * 40)
        print("        🎯 개발 기초 퀴즈 게임 🎯")
        print("=" * 40)
        print("  1. 퀴즈 도전하기")
        print("  2. 새 문제 등록")
        print("  3. 등록된 문제 보기")
        print("  4. 최고 기록 확인")
        print("  5. 문제 삭제")
        print("  0. 게임 종료")
        print("=" * 40)

    def play_quiz(self) -> None:
        """문제를 풀고 맞힌 개수를 계산한 뒤 최고 기록과 비교한다."""
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요.")
            return

        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        correct_count = 0

        # 저장된 목록은 건드리지 않고 복사한 목록만 섞기
        questions = self.quizzes.copy()
        random.shuffle(questions)

        for idx, quiz in enumerate(questions, start=1):
            print("-" * 40)
            quiz.display(idx)
            user_ans = self.prompt_int("정답 입력 (1-4): ", 1, 4)

            if quiz.is_correct(user_ans):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                print(f"❌ 오답입니다. 정답: {quiz.answer}번 - {quiz.choices[quiz.answer - 1]}")

        # 맞힌 비율을 100점 기준으로 계산
        total_questions = len(self.quizzes)
        score = int((correct_count / total_questions) * 100)

        print("\n" + "=" * 40)
        print(f"🏆 최종 점수: {score}점 / 100점")
        print(f"전체: {total_questions}문제 | 정답: {correct_count}개 | 오답: {total_questions - correct_count}개")

        if score > self.best_score:
            print(f"🎉 축하합니다! 새로운 최고 점수입니다! (기존: {self.best_score}점 ➔ 신규: {score}점)")
            self.best_score = score
            self.save_data()
        else:
            print(f"현재 최고 기록: {self.best_score}점")
        print("=" * 40)

    def add_quiz(self) -> None:
        """문제와 보기 네 개, 정답 번호를 받아 목록에 넣는다."""
        print("\n" + "-" * 40)
        print("📌 새로운 퀴즈를 추가합니다.")
        print("-" * 40)

        question = self.prompt_text("문제를 입력하세요: ")
        choices = []
        for i in range(1, 5):
            choice = self.prompt_text(f"선택지 {i}: ")
            choices.append(choice)

        answer = self.prompt_int("정답 번호 (1-4): ", 1, 4)

        new_quiz = Quiz(question=question, choices=choices, answer=answer)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("\n✅ 새로운 퀴즈가 성공적으로 추가 및 저장되었습니다!")

    def list_quizzes(self) -> None:
        """현재 보관 중인 문제와 각 문제의 보기를 확인한다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"[{idx}] {quiz.question}")
            for c_idx, choice in enumerate(quiz.choices, start=1):
                ans_mark = " (정답)" if c_idx == quiz.answer else ""
                print(f"    {c_idx}. {choice}{ans_mark}")
            print()
        print("-" * 40)

    def show_best_score(self) -> None:
        """지금까지 얻은 가장 높은 점수를 보여 준다."""
        print("\n" + "-" * 40)
        if self.best_score == 0:
            print("📊 아직 퀴즈를 완료한 기록이 없거나 최고 점수가 0점입니다.")
        else:
            print(f"🏆 현재 최고 점수: {self.best_score}점")
        print("-" * 40)

    def delete_quiz(self) -> None:
        """선택한 문제를 확인하고 동의한 경우에만 목록에서 제거한다."""
        if not self.quizzes:
            print("\n⚠️ 삭제할 퀴즈가 없습니다.")
            return

        print(f"\n🗑️ 삭제할 퀴즈 번호를 선택하세요 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"[{idx}] {quiz.question}")
        print("[0] 삭제 취소")
        print("-" * 40)

        target_idx = self.prompt_int("선택 (0~삭제할 번호): ", 0, len(self.quizzes))
        if target_idx == 0:
            print("삭제를 취소했습니다.")
            return

        print(f"선택한 문제: {self.quizzes[target_idx - 1].question}")
        confirm = self.prompt_int("삭제하시겠습니까? (1: 예, 0: 아니오): ", 0, 1)
        if confirm == 0:
            print("삭제를 취소했습니다.")
            return

        deleted_quiz = self.quizzes.pop(target_idx - 1)
        self.save_data()
        print(f"\n✅ [{target_idx}] '{deleted_quiz.question}' 퀴즈가 삭제되었습니다.")

    def run(self) -> None:
        """종료를 선택할 때까지 메뉴를 반복하고 중단 요청에도 대응한다."""
        print("\n🎮 개발 기초 퀴즈 게임에 오신 것을 환영합니다!")
        while True:
            try:
                self.display_menu()
                choice = self.prompt_int("선택 (0-5): ", 0, 5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_best_score()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 0:
                    print("\n게임을 종료합니다. 데이터를 안전하게 저장했습니다. 안녕히 가세요! 👋")
                    self.save_data()
                    break

            except (KeyboardInterrupt, EOFError):
                print("사용자에 의해 프로그램이 종료되었습니다.")
                print("데이터를 저장하고 프로그램을 종료합니다.")
                self.save_data()
                sys.exit(0)


if __name__ == "__main__":
    game = QuizGame(filepath="state.json")
    game.run()