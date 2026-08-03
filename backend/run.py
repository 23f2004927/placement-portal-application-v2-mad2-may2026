# 4 aug 26 updated
# Christiano Fernandes
# run.py
# server entry point


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
