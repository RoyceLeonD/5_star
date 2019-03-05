from services import *
def AddAsins():
    inserting = True
    output = []
    while inserting:
        print("What is the Amazon Product ID? :")
        #Example product: B017HW9DEW
        inputproducturl = input("product ID:   ")
        if inputproducturl:
            outdrop = inputproducturl
            output.append(outdrop)
        else:
            done = input("Are you done? Y/N   ")
            if done == 'Y':
                inserting = False

    return output
if __name__ == '__main__':
    ReadAsin(AddAsins())
    concat()