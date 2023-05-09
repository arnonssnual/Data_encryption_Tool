from neo4j import GraphDatabase


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    #return (True, result["password"]) or (False, None) for check_user is exits
    def check_user(self,username):
        @staticmethod
        def work(tx,username):
            query = (
                "MATCH (u:User) "
                "WHERE u.username = $username "
                "RETURN u.password AS password"
                
            )
            result = tx.run(query,username = username)
            return (result.single())
            
            
            #return data
            #return matched
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work, username)

        if result:
            return (True, result["password"])
        else:
            return (False, None)
        
    def check_user_email(self,email):
        @staticmethod
        def work(tx,email):
            query = (
                "MATCH (u:User) "
                "WHERE u.email = $email "
                "RETURN u.email AS email"
                
            )
            result = tx.run(query,email = email)
            return (result.single())
            
            
            #return data
            #return matched
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work, email)

        if result:
            return (True)
        else:
            return (False)
        


    #return True or False for enroll_user
    def enroll_user(self,username,password,email):
        @staticmethod
        def work(tx,username,password,email):
            query = (
            "MERGE (u:User{username: $username,password: $password,email: $email})"
            "ON CREATE SET u.createAt = timestamp()"
            "ON MATCH SET u.accessAt = timestamp()"
            "RETURN u"
            )
            result = tx.run(query, username = username,password = password,email = email)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work ,username,password,email)
            if (result == 1):
                App.link_to_key(self)
                return True
            else:
                return False
            
#When user is created, link to public key
    def link_to_key(self):
        @staticmethod
        def work(tx):
            query = (
                "MATCH (u:User) "
                "MATCH (pk:PublicKey) "
                "WHERE NOT (u)-[:OWNED]->(pk) "
                "MERGE (u)-[r:KNOWN]->(pk) "
                "Return r"
            )
            result = tx.run(query)
            return result
        with self.driver.session(database="neo4j") as session:
            result = (session.execute_write(work))

            return result
        
    #--------------------------------------------------------------
    #Meta data  management functions
    #--------------------------------------------------------------

    def file_owner(self,username):
        @staticmethod
        def work(tx,username):
            query = (
                "MATCH (u:User)-[r:OWNS]-(d:data) "
                "WHERE u.username = $username "
                "RETURN d"
            )
            result_list = []
            result = tx.run(query, username=username)
            for record in result:
                node = record['d']
                result_list.append(node.get('file_name'))
                #
            return result_list
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username)
            
            return result
    #get all file that shared to user
    def file_permission_access(self,username):
        @staticmethod
        def work(tx,username):
            query = (
                        "MATCH (u:User)<-[r:SHARED_TO]-(sk:SessionKey) "
                        "MATCH (d:data)<-[e:ENCRYPT]-(sk) "
                        "WHERE u.username = $username and not((sk)<-[:OWNED]-(u))"
                        "RETURN d ,sk.owner"
            )
            result_list = []
            result = tx.run(query, username=username)
            for record in result:
                filename = record['d']
                owner = record['sk.owner']
                result_list.append([filename.get('file_name'),owner])
                #
            return result_list
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username)
            

            return result
        #get all file that shared to user
    def file_shared_to(self,username):
            @staticmethod
            def work(tx,username):
                query = (
                            "MATCH (d:data)<-[e:ENCRYPT]-(sk:SessionKey)-[r:SHARED_TO]->(u:User) "
                            "WHERE sk.owner = $username and not((sk)<-[:OWNED]-(u))" 
                            "RETURN sk,d"
                )
                result_list = []
                result = tx.run(query, username=username)
                for record in result:
                    node_shared_to = record['sk']
                    node_filename = record['d']
                    result_list.append([node_filename.get('file_name'),node_shared_to.get('shared_to')])
                return result_list
            with self.driver.session(database="neo4j") as session:
                result = session.execute_read(work,username)
                

                return result
    def delete_access(self,username,filename):
        @staticmethod
        def work(tx,username,filename):
            query = (
                "MATCH (sk:SessionKey)-[:ENCRYPT]-(d:data) "
                "WHERE sk.shared_to = $username and d.file_name = $filename "
                "DETACH DELETE sk "
            )
            result = tx.run(query,username = username,filename = filename)
            return result.consume().counters.nodes_deleted
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,username,filename)
            if (result == 1):
                return True
            else:
                return False
            


    
    #check dupluiate file name in database and hashing
    def check_duplicate_file(self,username,filename):
        @staticmethod
        def work(tx,username,filename):
            query = (
                "MATCH (u:User)-[:OWNS]-(d:data) "
                "WHERE u.username = $username and d.file_name = $filename "
                "RETURN d"
            )
            result = tx.run(query,username = username,filename = filename)
            return result.single()
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username,filename)
            return result
        



    def multiple_key_check(self,username):
        @staticmethod
        def work(tx,username):
            query = (
                "MATCH (u:User)-[r:OWNED]->() "
                "WHERE u.username = $username " 
                "RETURN count(r) as count"
            )
            result = tx.run(query,username = username)
            result
            return result.single()['count']
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username)

        return result #Return number of Relation        
    


    def update_pb_key(self,username,keySize,k_value):
        @staticmethod
        def work(tx,username,keySize,k_value):
            query = (
                "MATCH (u:User)-[:OWNED]->(pb:PublicKey) "
                "WHERE u.username = $username AND pb.owner = $username "
                "SET pb.length = $keySize, pb.issuance = timestamp(), pb.value = $k_value "
                "RETURN pb"
            )
            result = tx.run(query, username = username,keySize = keySize,k_value = k_value)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,username,keySize,k_value)
            if (result == 1):
                return True
            else:
                return False
            


    def submit_pb_rsa(self,username,keySize,k_value):
        @staticmethod
        def work(tx,username,keySize,k_value):
            query = (
                "MATCH (u:User{username:$username}) "
                "MERGE (pb:PublicKey {type:'RSA',length:$keySize,owner:$username,issuance:timestamp(),value:$k_value}) "
                "MERGE (u)-[:OWNED]->(pb) "
                "RETURN pb"
            )
            result = tx.run(query, username = username,keySize = keySize,k_value = k_value)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,username,keySize,k_value)
            if (result == 1):
                App.link_to_key(self)
                return True
            else:
                return False
            

    def request_server_masterKey(self):
        @staticmethod
        def work(tx):
            query = (
                "MATCH (m:MasterKey) "
                "RETURN m"
            )
            result = tx.run(query)
            return result.single()
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work)
            return result
        

    
    def data_node(self,metadata,username,hashvalue):
        @staticmethod
        def work(tx,metadata,username,hashvalue):
            #create data_node with metadata ={Filename ,Filesize, Owner, Filetype, Issuance,hashvalue}
            file_name = metadata['name']
            filename = file_name.split("/")[1]
            file_size = metadata['size']
            file_type = metadata['type']
            issuance = metadata['gen']
            hashvalue = hashvalue

            query = (
                "MATCH (u:User{username:$username}) "
                "MERGE (data:data {owner:$username,file_name:$file_name,file_size:$file_size,file_type:$file_type,issuance:$issuance,hashvalue:$hashvalue}) "
                "MERGE (u)-[:OWNS]->(data) "
                "RETURN data"
            )
            result = tx.run(query,file_name=filename, file_size=file_size, file_type=file_type, issuance=issuance,username = username,hashvalue = hashvalue)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,metadata,username,hashvalue)
            if (result == 1):
                #App.link_to_key(self)
                return True
            else:
                return False
            
    def delete_file_inGCS(self,username,filename):
        @staticmethod
        def work(tx,username,filename):
            query = (
                "MATCH (u:User)-[:OWNS]-(d:data)<-[:ENCRYPT]-(sk:SessionKey) "
                "WHERE u.username = $username and d.file_name = $filename "
                "DETACH DELETE d ,sk"
            )
            result = tx.run(query,username = username,filename = filename)
            return result.consume().counters.nodes_deleted
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,username,filename)
            if (result == 1):
                return True
            else:
                return False
            

    def session_key_node(self,owner,iv,session_key,shared_to,filename):
        @staticmethod
        def work(tx,owner,iv,session_key,shared_to,filename):
            query = (
                "MATCH (owner:User{username:$owner}) " #Owmer of session key
                "MATCH (shared:User{username:$shared_to}) " #User that shared to
                "MATCH (d:data{file_name:$filename}) " #Data that shared to
                #in case that not shared to anyone shared_to = Owner
                "MERGE (s:SessionKey {owner:$owner,issuance:timestamp(),value:$session_key,iv:$iv,shared_to:$shared_to}) " #create session key node
                "MERGE (owner)-[:OWNED]->(s) " #create relation between owner and session key
                "MERGE (s)-[:SHARED_TO]->(shared) " #create relation between session key and shared_to
                "MERGE (s)-[:ENCRYPT]->(d) " #create relation between session key and data
                "RETURN s"
            )
            result = tx.run(query,owner = owner,session_key = session_key,iv = iv,shared_to = shared_to,filename = filename)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,owner,iv,session_key,shared_to,filename)
            if (result == 1):
                return True
            else:
                return False
            
    def session_key_node_for_owner(self,owner,iv,session_key,filename):
        @staticmethod
        def work(tx,owner,iv,session_key,filename):
            query = (
                "MATCH (owner:User{username:$owner}) " #Owmer of session key
                "MATCH (d:data{file_name:$filename}) " #Data that shared to
                #in case that not shared to anyone shared_to = Owner
                "MERGE (s:SessionKey {owner:$owner,issuance:timestamp(),value:$session_key,iv:$iv,shared_to:$shared_to}) " #create session key node
                "MERGE (owner)-[:OWNED]->(s) " #create relation between owner and session key
                "MERGE (s)-[:ENCRYPT]->(d) " #create relation between session key and data
                "MERGE (s)-[:SHARED_TO]->(owner) " #create relation between session key and shared_to
                "RETURN s "
            )
            result = tx.run(query,owner = owner,session_key = session_key,iv = iv,shared_to = owner,filename = filename)
            result = result.consume()
            result = result.counters.nodes_created
            return result
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(work,owner,iv,session_key,filename)
            if (result == 1):
                return True
            else:
                return False
            
    def request_session_key(self,username,filename):
        @staticmethod
        def work(tx,username,filename):
            query = (
                "MATCH (s:SessionKey)-[:ENCRYPT]-(d:data) "
                "WHERE s.shared_to = $username AND d.file_name = $filename "
                "RETURN s "
            )
            result = tx.run(query,username = username,filename = filename)
            return result.single()
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username,filename)
            return result
        

    def request_public_key(self,username):
        @staticmethod
        def work(tx,username):
            query = (
                "MATCH (u:User)-[:OWNED]->(pb:PublicKey) "
                "WHERE u.username = $username AND pb.owner = $username "
                "RETURN pb"
            )
            result = tx.run(query, username = username)
            return result.single()
        
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(work,username)
            return result