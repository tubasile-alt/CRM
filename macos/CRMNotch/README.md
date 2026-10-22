# CRM Notch

Aplicativo macOS que mantém a sala de espera do CRM junto ao notch. Ele usa a
mesma sessão e a mesma API do CRM: nenhum dado clínico é copiado para outro
serviço.

## Gerar o aplicativo

No Mac, execute:

```sh
cd macos/CRMNotch
chmod +x build-app.sh
./build-app.sh
open "dist/CRM Notch.app"
```

Na primeira abertura, use o ícone de duas pessoas na barra de menus e escolha
**Configurar endereço do CRM…**. Informe a URL completa do CRM. A janela de
login aparece dentro do app uma vez; depois disso, a sessão fica persistida.

Para testar sem gerar o pacote `.app`:

```sh
swift run CRMNotch --url http://127.0.0.1:5000
```

O app atualiza a lista a cada 30 segundos. Clique no notch para expandir, `Esc`
para recolher e em um paciente para abrir o prontuário no navegador padrão.
