#include <bits/stdc++.h>
using namespace std;
class Bucket;
class HashMap;
int M, B;
int occupancyThresold=75;
// Max # search keys in 1 block  = γ;
// Max # search keys in n blocks = n × γ    
// We have a total of:  r search keys  in n blocks       
// Avg occupancy = r/(n × γ)


class Bucket {
    public:
    Bucket *oFlow=NULL;
    vector<int> keys;


    Bucket * getBucket(){
        return new Bucket();
    }

    //Insert key in current bucket if not full else insert in overflow bucket
    void insertBucket(int key) {
        int totalKeys=keys.size();
        int buckCapacity=B/4;
        if(totalKeys < buckCapacity)
            keys.push_back(key);    
        else{
            //create overflow bucket
            if(oFlow)
                oFlow->insertBucket(key);
            else{
                oFlow=getBucket();
                oFlow->insertBucket(key);
            }    
        }        
        
    }

    //Check if current bucket contains key
    // if not check if it is in its overflow buckets
    bool contains(int key) {
        for (std::vector<int>:: iterator i = this->keys.begin(); i != this->keys.end(); ++i){
                if(*i==key)
                    return true;
        }
        Bucket *bucket = this->oFlow;
        while(1) {
            if(!bucket)
                break;
            for (std::vector<int>:: iterator i = bucket->keys.begin(); i != bucket->keys.end(); ++i){
                if(*i==key)
                    return true;
            }
            bucket=bucket->oFlow;
            
        }
        return false;
    }

};

Bucket * createBucket(){
    return new Bucket();
}

void changeBucket(vector<int> &v, Bucket * buck) {
        copy(buck->keys.begin(),buck->keys.end(), back_inserter(v)); 
        buck->keys.clear();
        while(buck->oFlow) {
            copy(buck->oFlow->keys.begin(), buck->oFlow->keys.end(), back_inserter(v)); 
            buck->oFlow->keys.clear();
            buck->oFlow=buck->oFlow->oFlow;
        }
}

class HashMap {
    vector<Bucket *> buckets;
    int totalKeys, rightBits;

    public:
    HashMap(){}
    HashMap(vector<Bucket *> &buckets,int totalKeys=0, int rightBits=1) {
        this->totalKeys=totalKeys;
        this->rightBits=rightBits;
        this->buckets=buckets;
    }

    void  addBucketOccupancy(){
        //add new buckets and perform rehashing
        vector<int> v;
        buckets.push_back(new Bucket());
        rightBits = ceil(log2((double)buckets.size()));
        // split old bucket and rehash
        int hashValue = buckets.size() - 1 - (1<<(rightBits - 1));
        changeBucket(v,buckets[hashValue]);
        for(int i = 0; i < v.size(); i++)
            buckets[hash(v[i])]->insertBucket(v[i]);
    }

    int hash(int key) {
        //if ( hash < n ) ==> real bucket
        int mod=(1<<rightBits);
        int hashValue=key%mod;
        if(hashValue<0)
            hashValue+=+mod;

        //else ( hash >= n ) ==> ghost bucket
        if(hashValue >= buckets.size())
            hashValue -= (1 << (rightBits - 1));
        return hashValue%mod;
    }


    bool insert(int x) {
        int hashValue = hash(x);
        //if value already present then return
        if(buckets[hashValue]->contains(x))
            return false;
        else{
            //otherwise insert key into hashed bucket
            buckets[hashValue]->insertBucket(x);
            totalKeys++;
            
            //calculate current occupancy
            int occupancy=100*(int)totalKeys*1.0/(buckets.size()*(B/4));//int of 4 bytes
            // if occupancy is greater than 75 percent increase bucket
            while(occupancy>=occupancyThresold){
                addBucketOccupancy();
                occupancy=100*(int)totalKeys*1.0/(buckets.size()*(B/4));//int of 4 bytes
            }
            return true;    
        }
        
    }

};


void proceedHashing(unsigned int MAX_OUTPUT_KEYS,vector<int> &inStream,vector<int> &outStream,HashMap &h) {
    for (std::vector<int>::iterator x = inStream.begin(); x != inStream.end(); ++x){
        int key=(*x);
        if(h.insert(key)) {
            if(outStream.size() == MAX_OUTPUT_KEYS) {
                //If output buffer is full print and clear it
                for (std::vector<int>::iterator i = outStream.begin(); i != outStream.end(); ++i)
                    cout << (*i) << '\n';
                outStream.clear();
            }
            outStream.push_back(key);
        }    
    }
    inStream.clear();
    
}

void isValidArgs(int arg){
    if(arg<4){
        cout<<"Provide correct parameters (input file, M, B)"<<endl;
        exit(-1);
    }
}

void read_File(const char* file_name,unsigned int MAX_INPUT_KEYS, unsigned int MAX_OUTPUT_KEYS,HashMap &h){
    FILE* file = fopen (file_name, "r");
    int inp = 0;
    vector<int> inStream;
    vector<int> outStream;
    fscanf (file, "%d", &inp);    
    while (!feof (file)){  
        //check if buffers have capacity
        if(inStream.size() < MAX_INPUT_KEYS)
            inStream.push_back(inp);
        else {
            //process the buffer if full
            proceedHashing(MAX_OUTPUT_KEYS,inStream,outStream,h);
            inStream.push_back(inp);
        }
        fscanf (file, "%d", &inp);      
    }
    //process the remaining buffer
    proceedHashing(MAX_OUTPUT_KEYS,inStream,outStream,h);
    //print the output of remaining buffer
    for (std::vector<int>::iterator i = outStream.begin(); i != outStream.end(); ++i)
        cout << (*i) << '\n';
    outStream.clear();
    fclose (file);        
}


int main(int argc, char *argv[]) {
    //check if correct arguments are provided
    //Assuming int is of 4 bytes and there are atleast 2 buffers and B>=4
    unsigned int MAX_INPUT_KEYS, MAX_OUTPUT_KEYS;
    isValidArgs(argc);

    char  *filename=argv[1];
    M = atoi(argv[2]); 
    B = atoi(argv[3]);

    // as sizeof(int) is 4
    MAX_INPUT_KEYS = B*(M-1)/4;
    MAX_OUTPUT_KEYS = B/4;

    vector<Bucket *> buckets;
    Bucket *buck1=createBucket();
    Bucket *buck2=createBucket();
    buckets.push_back(createBucket());
    buckets.push_back(createBucket());
    HashMap h=HashMap(buckets);
    //read file and process it
    read_File(filename,MAX_INPUT_KEYS,MAX_OUTPUT_KEYS,h);
    return 0;
}