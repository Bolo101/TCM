sentence = "This is a sentence"
print(sentence.split(sep="e"))
sentence_split = sentence.split()
sentence_joint = " ".join(sentence_split)
print(sentence_joint)

chain = ["This","is","a","good","sentence"]
print(chain)
print(chain[0])
print(chain[0][2])
chain2 = "This a pretty long sentence to cut"
chain2_split = chain2.split()
print(chain2_split)
print(" ".join(chain2_split))
test = """just want
to try this
out"""
print(test)
quote = "I am a \"pro developper\". Sick bro"
print(quote)

too_much_space = "              hello         "
print(too_much_space.strip())

print("A" in "Apple")

letter="A"
word = "Apple"

print(letter.lower() in word.lower())   #improved


movie = "Avenger"
print("My favorite movie is {}.".format(movie))
print("My favorite movie is %s." % movie)
print(f'My favorite movise is {movie}')
print("A".lower())

#Dictionary

category = {"Finance" : ["Ulysse","CryptoLedge"],"Sport":["Noel","Cbum"]}
print(category)
print(category["Finance"])
print(category["Finance"][0])


