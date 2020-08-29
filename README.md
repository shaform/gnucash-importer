# gnucash-importer
Utilities to import transactions into GnuCash


The gnucash-importer enables fast insertion of transactions into a [GnuCash](https://www.gnucash.org/) file. The program does not do any transaction matching or account matching so its speed is much faster than the importing tools provided by GnuCash itself. Typically, other scripts are used to generate the CSV files by converting the trasaction records downloaded from the bank. Then, the generated CSV files can be imported by `gnucash-importer` into the GnuCash file.

Note that the program does not automatically create the accounts or the currencies/commodities. You have to create those accounts in advance and the CSV should only contain existing accounts and existing commodities.

## Install Dependencies
This program requires [GnuCash Python bindings](https://wiki.gnucash.org/wiki/Python_Bindings). On Ubuntu/Debian systems, the easiest way to install Python bindings is as follows:

```bash
sudo apt install python3-gnucash
```

However, the system provided packages might be a bit outdated. To use the most updated version, we recommend compiling GnuCash from sources and setting up a [Conda environment](https://docs.conda.io/projects/conda/en/latest/index.html).

1. Firstly, set up a conda environment. Assume that this environment is set up at `$HOME/conda/envs/gnucash-importer`. Note that you need to make sure the Python version is the same as the GnuCash Python bindings. At the time of writing, the authors used Python 3.7.7.

2. Secondly, follow the [GnuCash Building Instructions](https://wiki.gnucash.org/wiki/Building_On_Linux) to install all the dependencies. When building the GnuCash, use the following commands to install the python bindings into the conda environment.

```bash
cd gnucash-4.<x>                          # cd into the source directory
mkdir build                               # create the build directory
cd build                                  # change into the build directory

# Set the installation direction to the conda enviroment we created, enable Python bindings
cmake -DCMAKE_INSTALL_PREFIX=$HOME/conda/envs/gnucash-importer -DWITH_PYTHON=True

make
make install
```

3. Finally, activate the conda environment. You can verify the installation by importing the gnucash package.

```bash
conda activate gnucash-importer
python

>>> import gnucash
```

## Usage

Use the following command to import all transactions in `CSV_FILE_PATH` into `GNUCASH_FILE_PATH`.

```bash
python -m gnucash_importer GNUCASH_FILE_PATH CSV_FILE_PATH
```

Note that you should not open the GnuCash file while importing because only one program can edit the file. Also, `gnucash-importer` does not do any matching currently, so **all valid transactions in the CSV file will be inserted into the GnuCash file even if they already existed**. Also note that the program will skip transactions that are imbalanced.

## CSV File Format

We use a file format similar to the GnuCash exported CSVs. In particular, the accepted fields are as follows:

- **date**
  - the date of the transaction, in mm/dd/yyyy format (e.g., `08/30/2020`)
- **description**
  - the description of the transaction (e.g., `Buy a laptop`)
- **commodity**
  - the main commodity/currency of the transaction, which is the unit of the **value** field (e.g., `CURRENCY::USD`)
- **account**
  - the account of the current split (e.g., `Assets:Assets:Current Assets:Cash Account:TD Ameritrade`)
- **memo**
  - a description of the current split
- **value**
  - value deposited into the account of the current split
- **amount**
  - when the target account has a different unit from the main commodity/currency, use the **amount** field to represent the converted amount deposited into the account

Similar to the GnuCash exported CSVs, **date**, **description**, and **commodity** only need to be specified once for each transaction. The splits of the transaction are represented by the other fields. An example CSV file is as follows:

```
date,description,commodity,memo,account,amount,value
09/24/2020,Purchase VTI,CURRENCY::USD,,Assets:Current Assets:Cash Account:TD Ameritrade,,-2500.00
,,,,Assets:Investments:Stock:VTI,10,2500.00
09/07/2020,BND Dividend,CURRENCY::USD,,Assets:Current Assets:Cash Account:TD Ameritrade,,70.00
,,,,Income:Dividend Income:Dividend Income USD:BND Dividend,,-100.00
,,,,Assets:Investments:Bond:BND,,
,,,W-8 Tax Withholding - BND,Expenses:Taxes:Federal:Taxes Withholding:Taxes Withholding USD:2020 Taxes Withholding USD,,30.00
```
Two transactions are represented by the above CSV file:

1. Purchase VTI
    - Account = Assets:Current Assets:Cash Account:TD Ameritrade
      - -2500.00 USD
    - Account = Assets:Investments:Stock:VTI
      - +2500.00 USD = (10 shares of VTI)
2. BND Dividend
    - Account = Assets:Current Assets:Cash Account:TD Ameritrade
      - +70.00 USD
    - Account = Income:Dividend Income:Dividend Income USD:BND Dividend
      - -100.00 USD
    - Account = Expenses:Taxes:Federal:Taxes Withholding:Taxes Withholding USD:2020 Taxes Withholding USD
      - +30.00 USD
      
Notice that the **value**s of all splits in a transaction must be summed to **0**. Otherwise, the transaction is imbalanced and would be ignored by the importer.

