# Protocol Buffers (Protobuf) — Quick Reference Guide

---

## What is Protocol Buffer?

Protocol Buffer (protobuf) is a way to **serialize structured data** — like JSON, but **smaller, faster, and strongly typed**. You define your data structure once in a `.proto` file, and it generates native code for any language you need.

> Think of it as: *"Define once, use everywhere — in any language, on any platform."*

---

## Why Use Protobuf Instead of JSON?

| Feature | JSON | Protobuf |
|---|---|---|
| Format | Human-readable text | Compact binary |
| Speed | Slower to parse | Much faster |
| Size | Larger | Up to 10× smaller |
| Type safety | No | Yes (strict types) |
| Code generation | No | Yes (auto-generated classes) |
| Language support | Universal | 10+ languages officially |

Protobuf is ideal when you need fast, efficient communication between services — which is exactly why **gRPC uses it as the default data format**.

---

## Core Concepts at a Glance

**Protobuf is made of four parts:**

1. **`.proto` file** — the schema you write (field names, types, service definitions)
2. **`protoc` compiler** — reads your `.proto` and generates code in your target language
3. **Generated classes** — native Python/Go/Java classes with serialization built-in
4. **Binary wire format** — the compact binary encoding used on the network or disk

---

## Writing a `.proto` File

```proto
edition = "2023";

message Person {
  string name = 1;
  int32  id   = 2;
  string email = 3;
}
```

Key rules:
- Every field has a **name**, a **type**, and a **field number** (e.g. `= 1`)
- Field numbers **cannot be reused or changed** once in production — they identify the field in binary encoding
- Use `repeated` for list/array fields
- Field names cannot contain dashes

---

## Field Types Supported

- **Primitives** — `string`, `int32`, `int64`, `bool`, `float`, `double`, `bytes`
- **Message** — nest another message as a field type (like a sub-object)
- **Enum** — a fixed set of named values
- **Oneof** — at most one field is set at a time (like a union)
- **Map** — key-value pairs (`map<string, int32>`)

---

## How protoc Code Generation Works

You run `protoc` **once at build time** — not on every request. It reads your `.proto` file and outputs source code files in your chosen language.

```
protoc --python_out=. --grpc_python_out=. user.proto
```

This generates (for Python):
- `user_pb2.py` — message classes with serialize/deserialize logic
- `user_pb2_grpc.py` — gRPC servicer (server) and stub (client) classes

You commit these generated files into your project like any other source file. You only re-run `protoc` when the `.proto` schema changes.

---

## Why Both Client AND Server Need protoc

This is a common question. Here is the simple answer:

Both sides need to understand the **same binary format**. The generated code is what teaches each side how to encode and decode messages.

```
user.proto  (shared contract — same file)
    │
    ├── protoc (server project, Python)
    │       └── user_pb2.py            ← message classes
    │       └── user_pb2_grpc.py       ← servicer base class (you implement this)
    │
    └── protoc (client project, Go)
            └── user.pb.go             ← message structs
            └── user_grpc.pb.go        ← client stub (call methods like local functions)
```

The server and client can be **completely different languages**. As long as both generated from the same `.proto`, the binary on the wire is compatible. That is the whole point — language-neutral by design.

---

## How a gRPC Request Works End-to-End

Here is what actually happens when your client calls `stub.GetUser(req)`:

```
CLIENT SIDE                              SERVER SIDE
──────────────────────────────────────────────────────────────
1. You create a message object           
   req = UserRequest(id=42)              

2. Generated stub serializes it          
   object → binary bytes                 

3. HTTP/2 sends binary over network ───► 4. gRPC receives binary bytes

                                         5. Generated code deserializes it
                                            binary → UserRequest object

                                         6. Your GetUser(request, ctx) runs
                                            → fetch DB, process data

                                         7. You return UserResponse(name="Alice")
                                            Generated code serializes it
                                            object → binary bytes

8. HTTP/2 sends binary back ◄─────────── 
   
9. Generated stub deserializes it
   binary → UserResponse object

10. Your app code reads: response.name
```

**Your application code never touches binary.** It only works with normal language objects. The generated code handles everything in between.

---

## Backward & Forward Compatibility

One of protobuf's best features — you can update your schema **without breaking existing services**.

- **Add a new field?** Old services just ignore it. New services read it fine.
- **Delete a field?** Old messages return the default value for that field.
- **Rule:** always `reserve` deleted field numbers so they are never accidentally reused.

```proto
message User {
  reserved 4;          // field 4 was deleted — number is now locked
  reserved "phone";    // field name also reserved
  string name = 1;
  int32  id   = 2;
}
```

---

## When NOT to Use Protobuf

Protobuf is great — but not for everything:

- **Data larger than a few MB** — protobuf loads the whole message into memory at once
- **Scientific float arrays** — formats like FITS are more efficient for large numerical data
- **Human-readable needs** — you cannot read binary protobuf without the `.proto` file
- **Standards-required environments** — protobuf is not an official open standard (unlike JSON/XML)
- **Simple public APIs** — JSON + REST is easier for third-party consumers without tooling

---

## The Complete Mental Model

```
Write .proto once
      │
      ▼
Run protoc at build time (one time per language, per project)
      │
      ├── Server: get base class → implement your logic
      └── Client: get stub → call methods like local functions
            │
            ▼
At runtime — every request:
  client object → [serialize] → binary → HTTP/2 → [deserialize] → server object
  server object → [serialize] → binary → HTTP/2 → [deserialize] → client object
```

---

## Quick Reference — Common protoc Commands

```bash
# Python (server + client)
protoc --python_out=. --grpc_python_out=. user.proto

# Go
protoc --go_out=. --go-grpc_out=. user.proto

# Java
protoc --java_out=. --grpc-java_out=. user.proto

# Multiple languages at once
protoc --python_out=./server --go_out=./client user.proto
```

---
