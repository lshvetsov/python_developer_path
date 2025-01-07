from flashcard import Flashcard
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flashcard import Base


class Tool:
    def __init__(self):
        engine = create_engine('sqlite:///flashcard.db?check_same_thread=False')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        self.flashcards: list[Flashcard] = []
        self.menu = {
            "1": ("Add flashcards", self.add_flashcards),
            "2": ("Practice flashcards", self.practice_flashcards),
            "3": ("Exit", self.exit_tool),
        }
        self.practice_menu = 'press "y" to see the answer:\npress "n" to skip:\npress "u" to update:\n'
        self.learning_menu = 'press "y" if your answer is correct:\npress "n" if your answer is wrong:\n'
        self.update_menu = 'press "d" to delete the flashcard:\npress "e" to edit the flashcard:\n'

    def add_flashcards(self):
        while (option := input("1. Add a new flashcard\n2. Exit\n")) != "2":
            if option == "1":
                while not (question := input("Question:\n").strip()):
                    ...
                while not (answer := input("Answer:\n").strip()):
                    ...
                flashcard = Flashcard(question=question, answer=answer, box=1)
                self.session.add(flashcard)
                self.session.commit()
            else:
                print(f"{option} is not an option")

    def practice_flashcards(self):
        self.flashcards = self.session.query(Flashcard).all()
        if self.flashcards:
            for card in self.flashcards:
                template = f'\nQuestion: {card.question}\n{self.practice_menu}'
                while (option := input(template)) not in ('y', 'n', 'u'):
                    print(f"{option} is not an option")
                if option == 'y':
                    print(f"\nAnswer: {card.answer}")
                    self.memorize_flashcards(card)
                elif option == 'u':
                    self.edit_flashcard(card)
        else:
            print("There is no flashcard to practice!")

    def memorize_flashcards(self, card):
        while (option := input(self.learning_menu)) not in ('y', 'n'):
            print(f"{option} is not an option")
        if option == 'y':
            card.box += 1
            if card.box >= 3:
                self.delete_card(card)
        elif option == 'n':
            card.box = 1
        self.session.commit()

    def edit_flashcard(self, card):
        while (option := input(self.update_menu)) not in ('d', 'e'):
            print(f"{option} is not an option")
        if option == 'd':
            self.delete_card(card)
        elif option == 'e':
            new_question = input(f"current question: {card.question}\nplease write a new question:\n").strip()
            new_answer = input(f"current answer: {card.answer}\nplease write a new answer:\n").strip()
            if new_question:
                card.question = new_question
            if new_answer:
                card.answer = new_answer
            self.save_flashcard(card)

    def main(self):
        while (option := self.get_option()) != "3":
            self.menu[option][1]() if option in self.menu else print(f"{option} is not an option")
        self.exit_tool()

    def get_menu(self):
        return "\n".join(f"{i}. {option[0]}" for i, option in self.menu.items())

    def get_option(self) -> str:
        return input(self.get_menu() + "\n")

    def exit_tool(self):
        self.session.close()
        print("Bye!")

    def delete_card(self, card):
        query = self.session.query(Flashcard)
        query.filter(Flashcard.id == card.id).delete()
        self.session.commit()

    def save_flashcard(self, card):
        query = self.session.query(Flashcard)
        query.filter(Flashcard.id == card.id).update({'question': card.question, 'answer': card.answer})
        self.session.commit()

def get_engine():
    return create_engine('sqlite:///flashcard.db?check_same_thread=False', echo=False)

if __name__ == '__main__':
    Tool().main()