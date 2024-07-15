from flask import Flask, jsonify
import hashlib
import json
from time import time
from uuid import uuid4

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.hash_block()

    def hash_block(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_data = []
        self.create_block(previous_hash='1', nonce=100)

    def create_block(self, previous_hash, nonce):
        block = Block(index=len(self.chain) + 1,
                      timestamp=time(),
                      data=self.current_data,
                      previous_hash=previous_hash,
                      nonce=nonce)
        self.current_data = []
        self.chain.append(block)
        return block

    def add_data(self, sender, recipient, amount):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_block):
        last_nonce = last_block.nonce
        last_hash = last_block.hash
        nonce = 0
        while not self.valid_proof(last_nonce, nonce, last_hash):
            nonce += 1
        return nonce

    @staticmethod
    def valid_proof(last_nonce, nonce, last_hash):
        guess = f'{last_nonce}{nonce}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    nonce = blockchain.proof_of_work(last_block)
    blockchain.add_data(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    previous_hash = last_block.hash
    block = blockchain.create_block(previous_hash, nonce)
    response = {
        'message': "New Block Forged",
        'index': block.index,
        'data': block.data,
        'previous_hash': block.previous_hash,
        'nonce': block.nonce,
        'hash': block.hash,
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [block.__dict__ for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) # use different ports if its already exits, example: port:5000, 5001,5003..

