
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
    #felan random khuruji mide
    sent = ABSA(comment,aspec)
    return  sent


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
    userReview= input("now write your review please ")
    aspec = []

    aspec = aspectExtractor(userReview)

    # negative aspects list
    negativeAspects = []
    for a in aspec:
        if aspectSentiment(userReview,a) == -1:
            print(a)
            negativeAspects.append(a)




    for i in range(0 ,len(asinsMeta)-1):
        if (asinsMeta[i]==productID):
           category = categoryMeta[i]
           break
   # print(category)

    productsInThatCategory=[]
    for j in range(0 , len(categoryMeta)-1):
        if categoryMeta[j] == category:
            productsInThatCategory.append(asinsMeta[j])


     # .1 of products to limit
    limitedProducts=[]
    # for m in range(0, int((len(productsInThatCategory) * 0.1))):
    for m in range(0 , 100):
        limitedProducts.append(productsInThatCategory[random.randrange
        (len(productsInThatCategory))])


    ratingAverage =(averageRating(limitedProducts))

    # products which average ratings for them is higher than 3.5
    highRatingProducts = []
    for i in range(0 , len(limitedProducts)):
        if ratingAverage[i] > 3.5:
            highRatingProducts.append(limitedProducts[i])

    recommendationList = []
    for h in range(0, len(highRatingProducts)):
        for j in range(0, len(reviewReview)):
            if highRatingProducts[h] == asinsReview[j]:

                for k in negativeAspects:
                  if k in reviewReview[j]:

                        reviewReview[j]=reviewReview[j].replace(k,'$t$')
                        if(aspectSentiment(reviewReview[j],k)== 1 or
                        aspectSentiment(reviewReview[j],k)) == 0:

                            recommendationList.append(asinsReview[j])
                            recommendationList = list(dict.fromkeys(recommendationList))
                        elif(listContains(recommendationList,asinsReview[j])):
                            recommendationList.remove(asinsReview[j] )
                            recommendationList = list(dict.fromkeys(recommendationList))
                  elif k not in reviewReview[j]:

                      recommendationList.append(asinsReview[j])
                      recommendationList = list(dict.fromkeys(recommendationList))

    print(highRatingProducts)
    print(len(highRatingProducts))
    print(len(limitedProducts))
    print(recommendationList)




#function to cal average rating of product
def averageRating(products):
    # average rating for each product
    ratings = []

    for p in products:
      sum=0
      counter=0
      for l in range(0 , len(asinsReview)):
          if ( asinsReview[l]==p):
              sum= sum+ overalReview[l]
              counter = counter+1
      if(sum !=0 and counter != 0):
        ratings.append( sum/counter)
      else:
          ratings.append(0)
    return  ratings




#function to search in dictionary
def search(values, searchFor):
    for k in values:
        if searchFor in k:
            return k
    return None


if __name__ == "__main__":

    asinsMeta = []
    categoryMeta = []
    also_viewedMeta = []
    file = open('amazonData/meta.strict', 'r')
    for f in file:
        productInfo = json.loads(f)
        k = productInfo['asin']
        asinsMeta.append(k)
        categoryMeta.append(productInfo['categories'])

    #    if(search(productInfo,'related')):
    #        related = productInfo['related']
    #        if(search(related,'also_viewed')):
    #            viewed = related['also_viewed']
    #            also_viewedMeta.append(viewed)
    #   else:
    #       also_viewedMeta.append(" ")

    asinsReview = []
    overalReview = []
    reviewReview = []
    reviewFile = open('amazonData/reviews_Cell_Phones_and_Accessories.json', 'r')
    for r in reviewFile:
        reviewInfo = json.loads(r)
        asinsReview.append(reviewInfo['asin'])
        overalReview.append(reviewInfo["overall"])
        reviewReview.append(reviewInfo["reviewText"])
    Rec()

