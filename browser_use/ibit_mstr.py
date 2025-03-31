import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np

# הורדת נתונים עבור IBIT ו-MSTR
ibit = yf.download('IBIT', start='2025-01-01')
mstr = yf.download('MSTX', start='2025-01-01')
print(ibit.columns)
# חישוב תשואות יומיות
ibit_returns = ibit[('Close', 'IBIT')].pct_change()
mstr_returns = mstr[('Close', 'MSTX')].pct_change()

# יצירת DataFrame משולב
returns_df = pd.DataFrame({
    'IBIT': ibit_returns,
    'MSTX': mstr_returns
})

# הסרת ערכים חסרים משני ה-DataFrames בו זמנית
returns_df = returns_df.dropna()

# יצירת גרף פיזור
plt.figure(figsize=(10, 6))
plt.scatter(returns_df['IBIT'], returns_df['MSTX'], alpha=0.5)
plt.xlabel('IBIT Daily Returns')
plt.ylabel('MSTX Daily Returns')
plt.title('IBIT vs MSTR Daily Returns')
plt.grid(True)

# חישוב קו מגמה
z = np.polyfit(returns_df['IBIT'], returns_df['MSTX'], 1)
p = np.poly1d(z)
plt.plot(returns_df['IBIT'], p(returns_df['IBIT']), "r--", alpha=0.8, label='Linear Regression - slope = ' + str(z[0]))

plt.legend()
plt.show()
