from agents.customer_support import customer_support

def main():
    response = customer_support.invoke({
        "messages": [
            ("human", "Qu'est ce que tu préfères ?"),
        ]
    })
    print(f"{response['messages'][-1].content}")


if __name__ == "__main__":
    main()
