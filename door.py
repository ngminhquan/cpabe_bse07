from cp_abe import cp_abe

def get_pw():
    count = input('Number of attributes:')
    attrs = []
    for i in range(int(count)):
        attrs.append(input('Enter your attributes: ').upper())
    return attrs

def main():
    #User enter attributes
    attrs = get_pw()
    ##verify attributes and generate OTP
    otp = cp_abe(attrs)
    return otp

if __name__ == '__main__':
    a = main()
    print(a)
