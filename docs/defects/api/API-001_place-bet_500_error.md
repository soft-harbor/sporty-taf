# Bug ID: API-001 - Server Returns 500 on Raw Binary Null-Byte Payload

* **Severity:** Medium / High (unhandled exception; potential DoS vector)
* **Reproduction Steps:**
  Shell `-d` flags strip null bytes, so use `--data-binary` to send a real null-byte payload:

  1. Create a temporary binary file containing a single null-byte:
     ```bash
     printf "\x00" > payload.bin
     ```
  2. Send this binary file to the bet placement endpoint using `curl` with the `--data-binary` flag:
     ```bash
     curl -X POST \
       -H 'x-user-id: candidate-BqxxUlex26' \
       -H 'Content-Type: application/json' \
       --data-binary @payload.bin \
       https://qae-assignment-tau.vercel.app/api/place-bet
     ```
  3. Clean up the temporary local file:
     ```bash
     rm payload.bin
     ```

* **Expected Result:**
  The server rejects non-JSON input with `400 Bad Request`.

* **Actual Result:**
  The JSON parser throws an unhandled exception and the server returns `500 Internal Server Error`:
  ```json
  {"error":"internal_server_error","message":"Unable to process request."}
