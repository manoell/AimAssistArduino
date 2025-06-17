import configparser
import os
import numpy as np

class ConfigManager:
    """
    Classe responsável por gerenciar configurações do programa.
    Facilita leitura/escrita de valores de diversos tipos no arquivo de configuração.
    """
    
    def __init__(self, config_file):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file (str): Caminho para o arquivo de configuração
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Verificar se o arquivo existe, se não existir criar com configurações padrão
        if not os.path.exists(config_file):
            self._create_default_config()
        else:
            self.config.read(config_file)
    
    def _create_default_config(self):
        """
        Cria um arquivo de configuração com valores padrão.
        """
        # Seção de conexão
        self.config['Connection'] = {
            'com_port': 'COM5',  # Porta COM padrão
            'baudrate': '115200'  # Taxa de transmissão padrão
        }
        
        # Seção de Aimbot
        self.config['Aimbot'] = {
            'fov': '100',          # FOV para detecção
            'x_speed': '0.4',      # Velocidade no eixo X
            'y_speed': '0.4',      # Velocidade no eixo Y
            'target_offset': '5.0', # Offset para mirar (cabeça)
            'smoothing': '0.7',    # Fator de suavização (0-1)
            'max_distance': '100',  # Distância máxima para auxiliar
            'history_length': '5'   # Tamanho do histórico para suavização
        }
        
        # Seção de cores para detecção
        self.config['Color'] = {
            'lower_color': '125,100,100',  # HSV inferior (púrpura)
            'upper_color': '155,255,255'   # HSV superior (púrpura)
        }
        
        # Seção de teclas
        self.config['Hotkeys'] = {
            'aim_key': '0x02',           # Botão direito (RMB)
            'aim_key_name': 'RMB',       # Nome para exibição
            'aim_toggle': 'F2',          # Tecla para ativar/desativar aimbot
            'reload': 'F4',              # Tecla para recarregar configurações
            'exit': 'F12'                # Tecla para sair
        }
        
        # Humanização
        self.config['Humanization'] = {
            'enabled': 'True',
            'base_reaction_time': '150',
            'reaction_time_variance': '50',
            'jitter_enabled': 'True',
            'jitter_strength': '0.3',
            'timing_variance_enabled': 'True',
            'min_timing_variance': '-0.5',
            'max_timing_variance': '2.0',
            'max_command_frequency': '500',
            'base_loop_delay': '5.0',
            'loop_delay_variance': '2.0',
            'simulate_fatigue': 'False',
            'simulate_attention_gaps': 'False',
            'natural_movement_curve': 'True'
        }
        
        # Salvar configurações padrão
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key):
        """
        Obtém um valor de string da configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            
        Returns:
            str: Valor da configuração
        """
        return self.config.get(section, key)
    
    def get_int(self, section, key):
        """
        Obtém um valor inteiro da configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            
        Returns:
            int: Valor inteiro da configuração
        """
        return self.config.getint(section, key)
    
    def get_float(self, section, key):
        """
        Obtém um valor float da configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            
        Returns:
            float: Valor float da configuração
        """
        return self.config.getfloat(section, key)
    
    def get_boolean(self, section, key):
        """
        Obtém um valor booleano da configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            
        Returns:
            bool: Valor booleano da configuração
        """
        return self.config.getboolean(section, key)
    
    def get_color(self, section, key):
        """
        Obtém um valor de cor (array numpy) da configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            
        Returns:
            numpy.ndarray: Array com valores RGB/HSV da cor
        """
        value = self.config.get(section, key)
        return np.array([int(x) for x in value.split(',')])
    
    def get_humanization_config(self):
        """
        Retorna todas as configurações de humanização
        
        Returns:
            dict: Configurações de humanização
        """
        try:
            return {
                'enabled': self.get_boolean('Humanization', 'enabled'),
                'base_reaction_time': self.get_float('Humanization', 'base_reaction_time') / 1000,  # Converter para segundos
                'reaction_time_variance': self.get_float('Humanization', 'reaction_time_variance') / 1000,
                'jitter_enabled': self.get_boolean('Humanization', 'jitter_enabled'),
                'jitter_strength': self.get_float('Humanization', 'jitter_strength'),
                'timing_variance_enabled': self.get_boolean('Humanization', 'timing_variance_enabled'),
                'min_timing_variance': self.get_float('Humanization', 'min_timing_variance') / 1000,
                'max_timing_variance': self.get_float('Humanization', 'max_timing_variance') / 1000,
                'max_command_frequency': self.get_int('Humanization', 'max_command_frequency'),
                'base_loop_delay': self.get_float('Humanization', 'base_loop_delay') / 1000,
                'loop_delay_variance': self.get_float('Humanization', 'loop_delay_variance') / 1000,
                'simulate_fatigue': self.get_boolean('Humanization', 'simulate_fatigue'),
                'simulate_attention_gaps': self.get_boolean('Humanization', 'simulate_attention_gaps'),
                'natural_movement_curve': self.get_boolean('Humanization', 'natural_movement_curve')
            }
        except:
            # Se seção não existir, retornar valores padrão
            return {
                'enabled': True,
                'base_reaction_time': 0.150,
                'reaction_time_variance': 0.050,
                'jitter_enabled': True,
                'jitter_strength': 0.3,
                'timing_variance_enabled': True,
                'min_timing_variance': -0.0005,
                'max_timing_variance': 0.002,
                'max_command_frequency': 500,
                'base_loop_delay': 0.005,
                'loop_delay_variance': 0.002,
                'simulate_fatigue': False,
                'simulate_attention_gaps': False,
                'natural_movement_curve': True
            }
    
    def set(self, section, key, value):
        """
        Define um valor na configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            value: Valor a ser definido (será convertido para string)
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
        self.save()
    
    def set_color(self, section, key, color_array):
        """
        Define um valor de cor na configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave do valor
            color_array (numpy.ndarray): Array com valores RGB/HSV
        """
        color_str = ','.join(str(x) for x in color_array)
        self.set(section, key, color_str)
    
    def save(self):
        """
        Salva as configurações atuais no arquivo.
        """
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def reload(self):
        """
        Recarrega as configurações do arquivo.
        """
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)