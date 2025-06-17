#!/usr/bin/env python3
"""
Teste do Sistema de Aim Assist Ultra-Otimizado
Script para verificar se todas as otimizações estão funcionando corretamente
"""

import time
import sys
from mouse_controller import MouseController

def test_connection():
    """Testa a conexão com o Arduino"""
    print("🔍 Testando conexão com Arduino...")
    
    try:
        controller = MouseController()
        print("✅ Conexão estabelecida com sucesso!")
        
        # Verificar informações do dispositivo
        if hasattr(controller.device, 'manufacturer') and hasattr(controller.device, 'product'):
            print(f"   Dispositivo: {controller.device.manufacturer} {controller.device.product}")
        
        # Verificar se está conectado
        if controller.is_connected():
            print("✅ Dispositivo está respondendo")
        else:
            print("❌ Dispositivo não está respondendo")
            return False
        
        controller.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def test_basic_movements():
    """Testa movimentos básicos do mouse"""
    print("\n🎮 Testando movimentos básicos...")
    
    try:
        controller = MouseController()
        
        # Teste de movimentos simples
        test_moves = [
            (1, 0, "Direita"),
            (0, 1, "Baixo"),
            (-1, 0, "Esquerda"),
            (0, -1, "Cima"),
            (5, 5, "Diagonal"),
            (-5, -5, "Diagonal inversa")
        ]
        
        success_count = 0
        for x, y, description in test_moves:
            if controller.move(x, y):
                print(f"✅ {description}: ({x}, {y})")
                success_count += 1
            else:
                print(f"❌ {description}: ({x}, {y})")
            
            time.sleep(0.1)  # Pequena pausa entre movimentos
        
        print(f"📊 Sucesso: {success_count}/{len(test_moves)} movimentos")
        
        controller.close()
        return success_count == len(test_moves)
        
    except Exception as e:
        print(f"❌ Erro nos movimentos: {e}")
        return False

def test_priority_movements():
    """Testa movimentos com prioridade (aimbot)"""
    print("\n🎯 Testando movimentos prioritários (aimbot)...")
    
    try:
        controller = MouseController()
        
        # Teste de movimentos prioritários
        priority_moves = [
            (2, -1, "Aimbot 1"),
            (3, 2, "Aimbot 2"), 
            (-1, 3, "Aimbot 3"),
            (4, -2, "Aimbot 4"),
            (-3, -1, "Aimbot 5")
        ]
        
        success_count = 0
        for x, y, description in priority_moves:
            if controller.move(x, y, priority=True):
                print(f"✅ {description}: ({x}, {y}) [PRIORIDADE]")
                success_count += 1
            else:
                print(f"❌ {description}: ({x}, {y}) [PRIORIDADE]")
            
            time.sleep(0.05)  # Pausa menor para teste de velocidade
        
        print(f"🎯 Sucesso prioritário: {success_count}/{len(priority_moves)} movimentos")
        
        controller.close()
        return success_count == len(priority_moves)
        
    except Exception as e:
        print(f"❌ Erro nos movimentos prioritários: {e}")
        return False

def test_performance():
    """Testa performance do sistema"""
    print("\n⚡ Testando performance do sistema...")
    
    try:
        controller = MouseController()
        
        # Teste de performance rápida
        start_time = time.time()
        commands_sent = 0
        target_commands = 100
        
        print(f"📤 Enviando {target_commands} comandos...")
        
        for i in range(target_commands):
            x = (i % 10) - 5  # Movimento de -5 a +4
            y = ((i + 5) % 10) - 5
            
            if controller.move(x, y, priority=(i % 5 == 0)):  # 20% prioritários
                commands_sent += 1
        
        # Aguardar processamento
        time.sleep(0.5)
        
        elapsed_time = time.time() - start_time
        commands_per_second = commands_sent / elapsed_time
        
        print(f"📊 Comandos enviados: {commands_sent}/{target_commands}")
        print(f"⚡ Velocidade: {commands_per_second:.1f} comandos/segundo")
        print(f"⏱️ Tempo total: {elapsed_time:.2f} segundos")
        
        # Obter estatísticas detalhadas
        stats = controller.get_performance_stats()
        print(f"📈 Taxa de sucesso: {stats['success_rate']*100:.1f}%")
        print(f"🎯 Comandos aimbot: {stats['aimbot_commands']}")
        print(f"⚡ Latência média: {stats['avg_latency_ms']:.1f}ms")
        print(f"🏃 Modo atual: {stats['current_timeout'].upper()}")
        
        controller.close()
        
        # Considerar sucesso se > 90% dos comandos foram enviados
        success_rate = stats['success_rate']
        return success_rate >= 0.9
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def test_click_functionality():
    """Testa funcionalidade de clique"""
    print("\n🖱️ Testando cliques...")
    
    try:
        controller = MouseController()
        
        # Teste de cliques
        click_tests = [
            (1, "Clique esquerdo"),
            (2, "Clique direito"),
            (4, "Clique meio"),
            (1, "Clique esquerdo prioritário (True)", True),
            (2, "Clique direito prioritário (True)", True)
        ]
        
        success_count = 0
        for test in click_tests:
            if len(test) == 3:
                button, description, priority = test
                success = controller.click(button, priority=priority)
            else:
                button, description = test
                success = controller.click(button)
            
            if success:
                print(f"✅ {description}")
                success_count += 1
            else:
                print(f"❌ {description}")
            
            time.sleep(0.1)
        
        print(f"🖱️ Sucesso em cliques: {success_count}/{len(click_tests)}")
        
        controller.close()
        return success_count == len(click_tests)
        
    except Exception as e:
        print(f"❌ Erro nos cliques: {e}")
        return False

def run_full_test():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DO SISTEMA DE AIM ASSIST")
    print("=" * 50)
    
    tests = [
        ("Conexão", test_connection),
        ("Movimentos Básicos", test_basic_movements),
        ("Movimentos Prioritários", test_priority_movements),
        ("Performance", test_performance),
        ("Cliques", test_click_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"💥 {test_name}: ERRO - {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Pausa entre testes
    
    # Relatório final
    print(f"\n{'='*50}")
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
    
    print(f"\n🏆 RESULTADO GERAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema está funcionando perfeitamente!")
        print("🎯 Sistema pronto para uso em aimbot!")
    elif passed >= total * 0.8:  # 80% ou mais
        print("⚠️ Maioria dos testes passou. Sistema funcional com algumas limitações.")
    else:
        print("❌ Muitos testes falharam. Verificar configuração do sistema.")
    
    return passed / total

if __name__ == "__main__":
    try:
        success_rate = run_full_test()
        
        print(f"\n📈 Taxa de sucesso geral: {success_rate*100:.1f}%")
        
        if success_rate >= 0.9:
            print("✅ Sistema aprovado para uso!")
            sys.exit(0)
        else:
            print("❌ Sistema precisa de ajustes!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro geral no teste: {e}")
        sys.exit(1)
