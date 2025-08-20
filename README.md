# EtherSeek

**EtherHide** is a blockchain-based technique for hiding malicious payloads within Ethereum smart contracts. Attackers leverage this to **deliver malware, exfiltrate data, or obfuscate C2 communications**.

`EtherSeek` is a cyber intelligence tool designed to identify and analyze the **EtherHide** technique. It extracts relevant **network information** from infected sites, enabling analysts to correlate suspicious activities to a crypto wallet.

## ✨ Features

* 🔗 **Correlate contracts and wallets** involved in suspicious operations given an infected page.
* 📡 **Extract network indicators** for threat intelligence workflows.
* 🛠 **Ad-hoc analysis tools** for customized blockchain research.
* 📑 **Export results** in analyst-friendly formats (JSON, CSV, etc.).


## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/m3ll0c/etherseek.git
cd etherseek
pip install -r requirements.txt
```

## 🚀 Usage

Basic command-line usage:

```bash
python etherseek.py [-h] (-f file column_name | -u api_key) [-o OUTPUT] [-r] -k KEYWORD [-w WALLETS] [-ci CHAINID] [-j JOBS] [-v]
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Open an issue with your idea or bug report.
2. Submit a pull request with clear commits and documentation.

## ⚖️ License

MIT License – see [LICENSE](LICENSE) for details.
