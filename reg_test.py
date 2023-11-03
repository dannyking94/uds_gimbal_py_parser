import re

def main():
    msg = ["flash read", "pitch Kp -1", "roll Ki 2.5"]
    pattern = '\d'

    output = re.findall(pattern, msg[0])
    print(output)

    output = re.findall('\d', msg[1])
    if len(output) > 0:
        pattern = r'(\D+)\s+(-?\d*\.?\d+)'
        output = re.findall(pattern, msg[1])[0]
    else:
        output = msg
    print(output)

    output = re.findall(pattern, msg[2])
    print(output)

if __name__ == '__main__':
    main()