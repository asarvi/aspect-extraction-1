from collections import defaultdict
from model.data_utils import CoNLLDataset
from model.aspect_model import ASPECTModel
from model.config import Config
from ABSA.example import ABSA
import tensorflow as tf
import json
import random

def align_data(data):

    spacings = [max([len(seq[i]) for seq in data.values()])
                for i in range(len(data[list(data.keys())[0]]))]
    data_aligned = dict()

    # for each entry, create aligned string
    for key, seq in data.items():
        str_aligned = ""
        for token, spacing in zip(seq, spacings):
            str_aligned += token + " " * (spacing - len(token) + 1)

        data_aligned[key] = str_aligned

    return data_aligned



def interactive_shell(model , sentence):
        words_raw = sentence.strip().split(" ")

        preds = model.predict(words_raw)
        to_print = align_data({"input": words_raw, "output": preds})


        aspects = aspectsToarray(words_raw ,preds )
        return aspects

#change B-A type to strings...
def aspectsToarray(sentence,preds):
    aspects = []
    for i in range(0 ,len(preds)-2):

        if(preds[i] == 'B-A' and preds[i+1] =='I-A' and preds[i+2] != 'I-A'):


            aspects.append(sentence[i] +" "+sentence[i+1])
        elif(preds[i] == 'B-A' and preds[i+1] =='I-A' and preds[i+2] == 'I-A'):

            aspects.append(sentence[i])
        elif( preds[i] =='B-A' and preds[i+1] =='O'):

            aspects.append(sentence[i])
        elif (preds[i] == 'B-A' and preds[i + 1] == 'B-A'):

            aspects.append(sentence[i] )
    if(preds[len(preds)-1] =='B-A'):
        aspects.append(sentence[len(preds)-1])
    if (preds[len(preds) - 2] == 'B-A'):
        aspects.append(sentence[len(preds) - 2])

    return  aspects

def aspectSentiment(comment ,aspec):
    sent = ABSA(comment,aspec)
    return sent


def aspectExtractor(sentence):
    # create instance of config
    config = Config()

    # build model

    model = ASPECTModel(config)
    model.build()
    model.restore_session(config.dir_model)

    # create dataset
    test  = CoNLLDataset(config.filename_test, config.processing_word,
                         config.processing_tag, config.max_iter)

    # evaluate and interact
    model.evaluate(test)
    preds=interactive_shell(model , sentence)
    return preds


def listContains(list , object):
    j =0
    for i in list:
        if object==i:
            j=1
    if j>0:
        return 1
    elif j==0:
        return 0

def Rec():
    productID = input("Type the product ID first ")
    userReview = input("now write your review please ")

    aspec = aspectExtractor(userReview)
    # negative aspects list
    negativeAspects = []

    for a in aspec:
        if aspectSentiment(userReview,a) == -1:
            print(a)
            negativeAspects.append(a)

    category = meta_category.get(productID)
    print(category)
    productsInThatCategory = []
    productsInThatCategory = category_dict.get(category)

    nice_products=[]
    for key in overall_dict:
        if (sum(overall_dict[key])/len(overall_dict[key])) > 4.5:
            nice_products.append(key)
    print(len(nice_products))

    highRatingProducts = []
    for m in range(0, 100):
    #for m in range(0, int((len(nice_products) * 0.1))):
        highRatingProducts.append(nice_products[random.randrange
        (len(nice_products))])

    recommendationList = []
    for h in highRatingProducts:
        reviews = reviews_dict.get(h)
        for n in negativeAspects:
             for rev in reviews:
                if n in rev:
                    rev = rev.replace(n, "$t$")
                    if (aspectSentiment(rev, n) == 1 or
                        aspectSentiment(rev, n) == 0):
                        # adds the object to the beginning of a set
                        recommendationList.insert(0,h)
                        recommendationList = list(dict.fromkeys(recommendationList))
                    elif (listContains(recommendationList, h)):
                        recommendationList.remove(h)
                        recommendationList = list(dict.fromkeys(recommendationList))
                elif n not in rev:
                        # adds the object to the end of list
                        recommendationList.append(h)
                        recommendationList = list(dict.fromkeys(recommendationList))

    #print(highRatingProducts)
   # print(len(highRatingProducts))
   # print(len(recommendationList))
    print(recommendationList)

# function to cal average rating of productfor m in range(0, int((len(nice_products) * 0.1))):
def averageRating(products):
    # average rating for each product
    ratings = []
    for product in products:
      rates = overall_dict.get(product)
      if rates != None:
          average = sum(rates)/len(rates)
          ratings.append(average)
      else:
          ratings.append(0)
    return ratings




#function to search in dictionary
def search(values, searchFor):
    for k in values:
        if searchFor in k:
            return k
    return None


if __name__ == "__main__":

    file = open('amazonData/meta.strict', 'r')
    meta_category = dict()
    category_dict = dict()
    for f in file:
        productInfo = json.loads(f)
        asin_meta = productInfo['asin']
        category = productInfo['categories']
        category = str(category).strip("[]")

        meta_category[asin_meta] = category

        category_dict.setdefault(category, []).append(asin_meta)

    # dictionary for reviews and overall

    reviews_dict = defaultdict(list)
    overall_dict = defaultdict(list)
    reviewFile = open('amazonData/reviews_Cell_Phones_and_Accessories.json', 'r')
    for r in reviewFile:
        reviewInfo = json.loads(r)
        reviews_dict[reviewInfo['asin']].append(reviewInfo["reviewText"])
        overall_dict[reviewInfo['asin']].append(reviewInfo["overall"])

    Rec()

