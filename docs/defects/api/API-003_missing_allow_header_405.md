# Bug ID: API-003 - 405 Response Missing Required `Allow` Header (RFC 9110 §15.5.6)

* **Severity:** Medium
* **Reproduction Steps:**
  Send an unsupported HTTP method (e.g. `TRACE`) and inspect response headers:

  1. Run `curl` with `-i` against any endpoint:
     ```bash
     curl -i -X TRACE -H 'x-user-id: candidate-BqxxUlex26' https://qae-assignment-tau.vercel.app/api/balance
     ```
  2. *(Optional)* Repeat for other endpoints:
     ```bash
     curl -i -X TRACE -H 'x-user-id: candidate-BqxxUlex26' https://qae-assignment-tau.vercel.app/api/matches
     curl -i -X TRACE -H 'x-user-id: candidate-BqxxUlex26' https://qae-assignment-tau.vercel.app/api/place-bet
     ```

* **Expected Result:**
  On `405 Method Not Allowed`, the response includes an `Allow` header listing supported methods (e.g. `Allow: GET` or `Allow: GET, POST`) per RFC 9110 §15.5.6.

* **Actual Result:**
  The server returns `405` with a plain-text body, but the `Allow` header is missing:
  ```text
  HTTP/2 405
  content-type: text/plain; charset=utf-8
  ... (other deployment/infrastructure headers) ...
  
  Method not allowed
  NOT_ALLOWED
  arn1::
