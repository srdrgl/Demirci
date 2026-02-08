# Demirci - Smart Rebar Cutting Optimizer

🏗️ Professional rebar cutting optimization tool using lexicographic optimization algorithm.

## Features

- ✂️ Multi-diameter rebar optimization
- 📊 Minimizes waste and number of bars
- 📁 Excel/CSV/ODS file import support
- 💾 Export to TXT, Excel, PDF
- 🎯 Adaptive efficiency algorithm
- 🖥️ User-friendly GUI interface

## Screenshots

![Main Interface](screenshots/1.png)
![inputs](screenshots/2.png)
![Results](screenshots/3.png)

## Installation

### Requirements
- Python 3.8+

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

### Basic Steps:
1. Enter rebar diameter, length, and quantity
2. Click "Add" or load from Excel
3. Click "Calculate"
4. View and export results

### Excel Import Format:
| Çap (mm) | Uzunluk (m) | Adet |
|----------|-------------|------|
| 12       | 3.5         | 10   |
| 16       | 5.2         | 8    |

## Algorithm

Uses **Lexicographic Optimization**:
1. **Phase 1**: Minimize number of bars
2. **Phase 2**: Minimize waste (if needed)

## Examples

See `/examples` folder for sample inputs and outputs.

## Technical Details

- **Solver**: OR-Tools (SCIP/CBC)
- **GUI**: Tkinter
- **Optimization**: Column Generation + Integer Programming

## License

MIT License

## 📝 Medium Article

Read the detailed article (Turkish): [Şantiyelerde Milyonlarca Dolarlık Fire: Demirci ile Çözüm](https://medium.com/@civileng.serdar/%C5%9Fantiyelerde-milyonlarca-dolarl%C4%B1k-fire-e79b38d069db)

*Learn about the financial and environmental impact of rebar cutting optimization in Turkish construction industry. The article covers real-world calculations showing how optimization can save millions of dollars and reduce carbon emissions.*

## Contact

📧 civileng.serdar@gmail.com  
🔗 [GitHub Profile](https://github.com/srdrgl)

## Contributing

Pull requests welcome! Please open an issue first.
