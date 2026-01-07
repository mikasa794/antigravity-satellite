
import lark_oapi.api.im.v1 as im_v1
import lark_oapi.api.im.v1.model as im_v1_model

print("--- Inspecting lark_oapi.api.im.v1 ---")
print(dir(im_v1))

print("\n--- Inspecting lark_oapi.api.im.v1.model ---")
print(dir(im_v1_model))

# specific check
print("\n--- Checking for GetMessageResourceReq ---")
if hasattr(im_v1, "GetMessageResourceReq"):
    print("Found in im.v1")
elif hasattr(im_v1_model, "GetMessageResourceReq"):
    print("Found in im.v1.model")
else:
    print("Not found in either. Checking partial matches...")
    for attr in dir(im_v1_model):
        if "MessageResource" in attr:
            print(f"Match in model: {attr}")
