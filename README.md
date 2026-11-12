# ChimpiBypass 🐵

Gerenciador experimental inspirado no Mesa3D para Windows, criado por Chimpi-hackintosh

## Recursos
- Selecionar aplicativo `.exe` e pasta Mesa3D
- Copiar `opengl32.dll` e opcionalmente `libgallium_wgl.dll` somente para a pasta do aplicativo
- Backup e restauração de DLLs
- Abrir o aplicativo selecionado
- Sem modificar drivers do Windows ou System32
- Recusa links simbólicos nos destinos e no backup para não seguir caminhos externos

## Limites
Não distribui Mesa3D. Use apenas bibliotecas de fontes confiáveis, com arquitetura compatível. Não garante FPS, suporte DirectX ou compatibilidade completa. Evite instalar em pastas de sistema

## Compilação
Execute `build-windows.bat` ou use o GitHub Actions. Ao enviar uma tag `v1.0.0`, o workflow compila `ChimpiBypass.exe` e tenta anexá-lo numa Release de pré-lançamento. O binário ainda precisa de testes reais
