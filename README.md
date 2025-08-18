# etherseek

**EtherHide** is a blockchain-based technique for hiding malicious payloads within Ethereum smart contracts. Attackers leverage this to **deliver malware, exfiltrate data, or obfuscate C2 communications**.

`etherseek` is a cyber intelligence tool designed to identify and analyze the **EtherHide** technique. It extracts relevant **network information** from infected sites, enabling analysts to correlate suspicious activity across the blockchain. Usefull to map active and past campaigns.

## ✨ Features

* 🔍 **Detect EtherHide usage** in Ethereum|BNB contracts.
* 🔗 **Correlate contracts and wallets** involved in suspicious operations.
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
python etherseek.py --sites-list infected.csv --export-raw results.json --export results.csv --profiles-cleanup
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Open an issue with your idea or bug report.
2. Submit a pull request with clear commits and documentation.

## ⚖️ License

MIT License – see [LICENSE](LICENSE) for details.
