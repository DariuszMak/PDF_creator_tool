import os


def hello_world():
    return "Hello world!"

def main():
    try:
        msg = hello_world()
        print(msg)        
    except Exception:
        msg = f'Error! during App start: "{e}"'
        print(msg)
        os._exit(1)


if __name__ == '__main__':
    main()