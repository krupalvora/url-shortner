from hashids import Hashids
url_id=14
hashids = Hashids(min_length=4, salt='dada bhagwan')
hashid = hashids.encode(url_id)
print(hashid)
id=hashids.decode(hashid)
print(id)