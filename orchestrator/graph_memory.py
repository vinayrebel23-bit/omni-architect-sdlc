from neo4j import GraphDatabase
import os

class EpistemicGraphMemory:
    def __init__(self):
        # Connect to the local Neo4j Docker container
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        if not uri or not user or not password:
            print("[!] Neo4j credentials are unset. Refusing to use a default password.")
            self.connected = False
            self.driver = None
            return

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.connected = True
            print("[GraphMemory] Successfully connected to Neo4j Epistemic Graph.")
        except Exception as e:
            print(f"[!] Neo4j Connection Failed: {e}")
            self.connected = False

    def close(self):
        if self.connected:
            self.driver.close()

    def query_dependencies(self, target_file: str) -> str:
        """
        Executes a Cypher query to retrieve the AST topology and attached ADRs 
        for a specific file or function.
        """
        if not self.connected:
            return f"Mock Graph Context: {target_file} depends on DatabaseModule. (Graph DB Offline)"

        cypher_query = """
        MATCH (f:File {name: $file_name})-[:DEPENDS_ON]->(dep:File)
        OPTIONAL MATCH (f)-[:HAS_ADR]->(adr:ArchitectureDecision)
        RETURN f.name AS File, collect(dep.name) AS Dependencies, collect(adr.summary) AS Decisions
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, file_name=target_file)
                record = result.single()
                
                if record:
                    context = f"Topological Context for {target_file}:\n"
                    context += f"- Dependencies: {', '.join(record['Dependencies'])}\n"
                    context += f"- Architecture Decisions: {', '.join(record['Decisions'])}\n"
                    return context
                else:
                    return f"No graph topology found for {target_file}."
        except Exception as e:
            print(f"[!] Cypher Query Error: {e}")
            return f"Error retrieving graph context."

# Singleton instance for the orchestrator
graph_db = EpistemicGraphMemory()

if __name__ == "__main__":
    # Test the Graph Retrieval
    context = graph_db.query_dependencies("src/auth/login.js")
    print(context)
    graph_db.close()
