import gzip
import pickle
import io

file_path = "similarity.pkl.gz"

try:
    # open gzip file safely
    with gzip.open(file_path, "rb") as f:
        file_content = f.read()  # read raw bytes first

    # load pickle from bytes buffer
    sim = pickle.load(io.BytesIO(file_content))

    print("✅ File loaded successfully!")
    print("Type:", type(sim))
    try:
        print("Length:", len(sim))
    except Exception:
        print("Length: N/A (not a list or array)")

except EOFError:
    print("❌ EOFError: file seems truncated or compressed incorrectly.")
except Exception as e:
    print("❌ Error while loading file:", e)

