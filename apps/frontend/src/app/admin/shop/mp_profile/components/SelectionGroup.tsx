'use client';

import { SelectableOption } from '../types';

interface SelectionGroupProps {
  title: string;
  options: SelectableOption[];
  selected: string | string[];
  onSelect: (value: string) => void;
  multiSelect?: boolean;
  coloredOptions?: boolean;
}

const skinToneColors: Record<string, string> = {
  porcelain: 'bg-[#F5E6D3]',
  fair: 'bg-[#F4D7BA]',
  medium: 'bg-[#D8A882]',
  tan: 'bg-[#C68552]',
  olive: 'bg-[#9D6B3B]',
  deep: 'bg-[#7B4B2A]',
  dark: 'bg-[#5D3520]',
  ebony: 'bg-[#3D2416]',
};

export default function SelectionGroup({
  title,
  options,
  selected,
  onSelect,
  multiSelect = false,
  coloredOptions = false,
}: SelectionGroupProps) {
  const isSelected = (optionId: string) => {
    if (Array.isArray(selected)) {
      return selected.includes(optionId);
    }
    return selected === optionId;
  };

  return (
    <div className="mb-6">
      <h3 className="text-center font-semibold text-base mb-3">{title}</h3>
      <div className="flex flex-wrap justify-center gap-2 px-4">
        {options.map((option) => {
          const selected = isSelected(option.id);
          return (
            <button
              key={option.id}
              onClick={() => onSelect(option.id)}
              className={`
                px-4 py-2 rounded-full text-sm font-medium transition-colors
                ${
                  selected
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
                ${coloredOptions ? 'flex items-center gap-2' : ''}
              `}
            >
              {coloredOptions && skinToneColors[option.id] && (
                <span
                  className={`w-5 h-5 rounded-full border border-gray-300 ${skinToneColors[option.id]}`}
                />
              )}
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
