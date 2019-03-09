import json, os
import random
"""
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

"""
class stakeholder_ratings():
    def ratings(self):
        with open('static/data_file.json', 'r') as f:
            ratings_break_down = json.load(f)["ratings"]
        rating = []
        for ratings in ratings_break_down:
            temp_val = ratings_break_down[ratings]
            temp_val = temp_val[:temp_val.rfind("%")]
            temp_val = int(temp_val)
            #print(temp_val)
            rating += [temp_val]

        raw_rating = 0
        ranting_bank = [5,4,3,2,1]
        for i in [0,1,2,3,4]:
            raw_rating += ranting_bank[i]*rating[i]

        return raw_rating/100

    def main_stakeholder_bucketing(self):
        raw_rating = self.ratings()
        def draw_rand():
            return round(random.uniform(float(raw_rating)-float(1), float(5)), 2)
        print(raw_rating)
        fulfillment = draw_rand()
        print(fulfillment)
        product_quality = draw_rand()
        service = draw_rand()
        usability = draw_rand()
        table = {
            "raw_rating":raw_rating,
            "fulfillment":fulfillment,
            "product_quality":product_quality,
            "servce":service,
            "usability":usability
        }
        print(table)

        with open('static/ratings.json','w') as outfile:
            json.dump(table,outfile)
        
 

print(stakeholder_ratings().main_stakeholder_bucketing())