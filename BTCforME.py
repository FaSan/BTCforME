import subprocess
import urllib2
import twitter
import codecs
import string
import json
import os

#    api instances
twitter_search = twitter.Twitter(domain="search.twitter.com")

#    relative basePath
basePath = os.path.dirname(os.path.abspath(__file__))

#    userIDs
userIDs = " "
usersPath = basePath + '\\users.txt'

if os.path.isfile(usersPath) and usersPath.endswith('.txt'):
    #   read previously made users file
    readObject = open(usersPath,'r')
    userIDs = readObject.read()
    readObject.close()
else:
    #    create new users file
    writeObject = codecs.open(usersPath,'w')
    writeObject.write(userIDs)
    writeObject.close()

#    addresses
addresses = " "
addressesPath = basePath + '\\addresses.txt'

if os.path.isfile(addressesPath) and addressesPath.endswith('.txt'):
    #   read previously made addresses file
    readObject = open(addressesPath,'r')
    addresses = readObject.read()
    readObject.close()
else:
    #    create new addresses file
    writeObject = codecs.open(addressesPath,'w')
    writeObject.write(addresses)
    writeObject.close()
    
#    search results
search_results = []

#   get the search results
for page in range(1,2):
    print "Page %d" % page
    search_results.append(twitter_search.search(q="I want some @BTCForMe #bitcoin",rpp=100,page=page))

#    strip out unused data
tweeters = [ [ r['text'],r['from_user_id'] ] \
	for result in search_results \
		for r in result['results'] ]

#    new addresses
newAddresses = ""
        
#    filter duplicates
for text, userid in tweeters:
    findString = " " + str(userid) + " "
    if userIDs.find(findString) < 0:
        userIDs = userIDs + str(userid) + " "
        words = text.split(" ")
        for word in words:
            word = word.strip()
            if len(word) > 26 and len(word) < 35:
                if word.find('1') == 0 or word.find('3') == 0:
                    sanitizeAddress = ""
                    findString = " " + word + " "
                    base58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
                    for char in base58:
                        sanitizeAddress = sanitizeAddress.replace(char, "")
                    if len(sanitizeAddress) == 0 and addresses.find(findString) < 0 and newAddresses.find(findString) < 0:
                        #   Appears Valid
                        newAddresses = newAddresses + word + " "
                        break
                        
#   prepare recipients
recipients = '{'
satoshisPerAddress = .00000001

#   insanity
if len(newAddresses) > 26:
    addressArray = newAddresses.split(" ")
    
    #   add address and satoshis
    for address in addressArray:
        if len(address) > 26:
            recipients = recipients + '"' + address + '":' + str( "%.8f" % satoshisPerAddress ).replace(".", "") + ','
    
    #   end prep
    recipients = recipients[:recipients.__len__() - 1] + '}'
    
    #   post - note: transaction fees are applied automatically.
    stringURL = "https://blockchain.info/merchant/INSERT HEXIDECIMAL PRIVATE KEY HERE/sendmany?recipients="
    response = json.loads( urllib2.urlopen(stringURL + urllib2.quote( recipients )).read() )
    
    #   WTFHappened???
    if 'error' in response:
        print "Error: " + response['error']
    else:
        print "Message: " + response['message']
        print "tx_hash: " + response['tx_hash']
        
        #    write new userIDs
        writeObject = codecs.open(usersPath,'w')
        writeObject.write(userIDs)
        writeObject.close()
        
        #    write new addresses
        writeObject = codecs.open(addressesPath,'w')
        writeObject.write(addresses + newAddresses)
        writeObject.close()
else:
    print "No new users/addresses"