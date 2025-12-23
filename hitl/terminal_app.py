from autogen_runner import run_agent_sync

import time 



def main():

    while True:

        user = input("\n\n\tUser: ")

        print()

        if user == "exit":
            break 

        print("Agent is thinking...")

        response = run_agent_sync(user, list())

        print("Wait for 10 seconds.")

        time.sleep(10)
        
        print(response)

        

if __name__ == "__main__":

    main()







