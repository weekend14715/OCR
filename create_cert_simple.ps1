# Create Self-Signed Certificate for Code Signing
Write-Host "Creating Self-Signed Certificate..." -ForegroundColor Green

# Create certificate
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=OCR License System" -KeyUsage DigitalSignature -FriendlyName "OCR License System Code Signing" -CertStoreLocation "Cert:\CurrentUser\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")

# Export to PFX file
$password = ConvertTo-SecureString -String "123456" -Force -AsPlainText
$certPath = "Cert:\CurrentUser\My\$($cert.Thumbprint)"
Export-PfxCertificate -Cert $certPath -FilePath "MyCert.pfx" -Password $password

Write-Host "Certificate created successfully!" -ForegroundColor Green
Write-Host "Certificate file: MyCert.pfx" -ForegroundColor Yellow
Write-Host "Password: 123456" -ForegroundColor Yellow
Write-Host "Thumbprint: $($cert.Thumbprint)" -ForegroundColor Yellow

