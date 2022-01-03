import argparse
import csv
import logging
import os
import shlex
import subprocess

from app import values
from app.lib import db, file, exceptions


LOGGING_LEVEL = os.environ.get(
    'GENERATE_PRETABLE_LOGGING_LEVEL',
    'INFO'
)

PROCESSED_LOGS_DIRECTORY = os.environ.get(
    'GENERATE_PRETABLE_PROCESSED_LOGS_DIRECTORY',
    'data/processed/'
)

OUTPUT_DIRECTORY = os.environ.get(
    'OUTPUT_DIRECTORY',
    'data/pretables/'
)

UNSORTED_POSFIX = os.environ.get(
    'GENERATE_PRETABLE_UNSORTED_POSFIX',
    'unsorted'
)

COLLECTION = os.environ.get(
    'GENERATE_PRETABLE_PARSE_LOG_COLLECTION',
    'scl'
)

STR_CONNECTION = os.environ.get(
    'GENERATE_PRETABLE_PARSE_LOG_STR_CONNECTION',
    'mysql://user:pass@localhost:3306/usage'
)

UNSORTED_PRETABLES_DIRECTORY = os.environ.get(
    'GENERATE_PRETABLE_UNSORTED_PRETABLES_DIRECTORY',
    'data/unsorted_pretables/'
)


def _args_to_param(args, ignore):
    params = {}
    for k, v in args.__dict__.items():
        if k not in ignore:
            params[k] = v
    return params


def extract_values(data, header, delimiter):
    """Método auxiliar para extrair valores de um dicionário usando chaves indicadas em um header.

    Parameters
    ----------
    data : dict
        Dicionário de dados
    header : list
        Chaves cujos valores serão usados para extrair os dados
    delimiter: str
        Caractere utilizado para agrupar itens em uma string

    Yields
    ------
    str
        Uma string delimitada por join_char que representa os valores obtidos de data
    """
    return delimiter.join([data.get(h) for h in header])


def generate_pretables(
    parsed_file, 
    output_directory, 
    header=values.PRETABLE_FILE_HEADER, 
    extension='tsv', 
    delimiter='\t'
):
    """
    Gera arquivo(s) com os dados de log processados.
    Grava um arquivo por dia.

    Parameters
    ----------
    parsed_file : str
        Nome do arquivo contendo dados de log processados
    output_directory : str
        Caminho no disco em que o arquivo será gravado
    header : list
        Lista de nomes de campos a serem gravados no arquivo de pré-tabela
    extension : str
        Extensão do nome dos arquivos a serem gerados
    delimiter : str
        Separador de colunas dos arquivos a serem gerados
    """
    logging.info('Lendo %s' % parsed_file)
    with open(parsed_file) as fin:
        output_files = {}

        csv_reader = csv.DictReader(fin, delimiter=delimiter)

        try:
            for row in csv_reader:
                # obtém yyyy-mm-dd do acesso
                ymd = row.get('serverTime').split(' ')[0]

                # gera nome de arquivo relacionado a ymd
                ymd_output_path = file.generate_filepath_with_filename(
                    directory=output_directory,
                    filename=ymd,
                    posfix=UNSORTED_POSFIX,
                    extension=extension,
                )

                # verifica se arquivo já existe
                if not os.path.exists(ymd_output_path):
                    logging.info('Criado arquivo %s' % ymd_output_path)
                    file.create_file_with_header(ymd_output_path, header)

                # abre arquivo em modo append, caso ainda não esteja aberto. adiciona em dicionário uma referência ao arquivo
                if ymd not in output_files:
                    output_files[ymd] = open(ymd_output_path, 'a')

                # obtém uma linha moldada ao formato pré-tabela
                fmt_values = extract_values(row, header, delimiter)

                # grava linha no arquivo de data correta
                output_files[ymd].write(fmt_values + '\n')

        finally:
            # garante fechamento dos arquivos
            for v in output_files.values():
                v.close()

        return output_files


def generate_pretables_db(
    str_connection, 
    collection, 
    output_directory, 
    header=values.PRETABLE_FILE_HEADER, 
    extension='tsv', 
    delimiter='\t', 
    processed_logs_directory=PROCESSED_LOGS_DIRECTORY,
):
    non_pretable_dates = db.get_non_pretable_dates(str_connection, collection)

    for npt in non_pretable_dates:
        processed_files = file.get_processed_files(npt, processed_logs_directory)
        output_files = {}

        for pf in processed_files:
            pf_results = generate_pretables(parsed_file=pf, output_directory=output_directory, header=header, extension=extension, delimiter=delimiter)
            output_files.update(pf_results)

        for k in output_files:
            db.set_control_date_status(str_connection, collection, k, values.DATE_STATUS_EXTRACTING_PRETABLE)
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-o',
        '--output_directory',
        default=OUTPUT_DIRECTORY,
        help='Diretório de saída',
    )

    subparsers = parser.add_subparsers(
        title='mode',
    )

    file_parser = subparsers.add_parser('file', help='Modo de caminho de arquivo')

    file_parser.add_argument(
        '-f',
        '--parsed_file',
        help='Caminho de arquivo de log processado',
    )

    database_parser = subparsers.add_parser('database', help='Modo de banco de dados')

    database_parser.add_argument(
        '-u', 
        '--str_connection',
        default=STR_CONNECTION,
        help='String de conexão com banco de dados',
    )
    
    database_parser.add_argument(
        '-c', 
        '--collection',
        default=COLLECTION,
        help='Acrônimo de coleção',
    )

    database_parser_subparsers = database_parser.add_subparsers(title='command')

    database_parser_subparsers_generate = database_parser_subparsers.add_parser('generate')

    database_parser_subparsers_generate.add_argument(
        '-p',
        '--processed_logs_directory',
        default=PROCESSED_LOGS_DIRECTORY,
        help='Diretório de arquivos de log pré-processados'
    )

    database_parser_subparsers_sort = database_parser_subparsers.add_parser('sort')

    database_parser_subparsers_sort.add_argument(
        '-t',
        '--unsorted_pretables_directory',
        default=UNSORTED_PRETABLES_DIRECTORY,
        help='Diretório de pré-tabelas não ordenadas'
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=LOGGING_LEVEL,
        format='[%(asctime)s] %(levelname)s %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
    )

    check_dir(params.output_directory)

    generate_pretables(
        input_file=params.input_file,
        output_directory=params.output_directory,
        header=PRETABLE_FILE_HEADER,
        extension='tsv',
        delimiter='\t',
    )
