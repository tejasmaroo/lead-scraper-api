from apollo_filter_generator import ApolloFilterGenerator

def main():
    generator = ApolloFilterGenerator()
    
    print("Apollo.io Lead Filter Generator")
    print("-------------------------------")
    print("Example query: 'Find importers from USA to India'")  # Updated example
    print("Example query: 'VP of Finance in small companies based in New York'")
    print("Example query: 'Marketing managers in medium-sized tech companies'")
    print()
    
    # Example query
    query = input("Enter your search query: ")
    
    # Generate URL
    url = generator.generate_filter_url(query)
    
    print("\n=== Generated Apollo.io URL ===")
    print(url)

if __name__ == "__main__":
    main()
