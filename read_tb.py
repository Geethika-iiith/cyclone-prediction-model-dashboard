try:
    with open('tb.txt', 'r') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading tb.txt: {e}")
